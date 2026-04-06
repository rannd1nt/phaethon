use pyo3::prelude::*;
use pyo3::types::PyList;
use pyo3::exceptions::PyValueError;
use std::collections::HashMap;

type UnitMetadata = (f64, f64, Option<f64>, Option<f64>);

// The Zero-Allocation Physical String Parser
fn parse_physical_string(text: &str) -> (f64, Option<&str>) {
    let trimmed = text.trim();
    if trimmed.is_empty() || trimmed.eq_ignore_ascii_case("nan") || trimmed.eq_ignore_ascii_case("none") {
        return (f64::NAN, None);
    }
    
    // 1. JALUR CEPAT: Jika ada spasi, langsung pisahkan.
    if let Some(idx) = trimmed.find(char::is_whitespace) {
        let num_part = trimmed[..idx].trim();
        let unit_part = trimmed[idx..].trim_start();
        let num = num_part.parse::<f64>().unwrap_or(f64::NAN);
        return (num, if unit_part.is_empty() { None } else { Some(unit_part) });
    }
    
    // 2. JALUR KETAT: String menempel (Misal "120K" atau "1.5e3V" atau polos "120")
    let bytes = trimmed.as_bytes();
    let mut split_idx = trimmed.len();
    
    for (i, &b) in bytes.iter().enumerate() {
        let c = b as char;
        // Deteksi huruf atau simbol (°, %)
        if c.is_ascii_alphabetic() || !c.is_ascii() || c == '%' {
            // SENTRY GUARD: Lindungi Scientific Notation!
            // Jika hurufnya 'e' atau 'E', cek apakah ada angka atau +/- setelahnya.
            if (c == 'e' || c == 'E') && i > 0 && i + 1 < bytes.len() {
                let next_c = bytes[i + 1] as char;
                if next_c.is_ascii_digit() || next_c == '+' || next_c == '-' {
                    continue; // Lewati! Ini bagian dari angka, bukan unit.
                }
            }
            split_idx = i;
            break;
        }
    }
    
    let num_part = &trimmed[..split_idx];
    let unit_part = &trimmed[split_idx..];
    
    let num = num_part.parse::<f64>().unwrap_or(f64::NAN);
    let unit = if unit_part.is_empty() { None } else { Some(unit_part) };
    
    (num, unit)
}

#[pyfunction]
#[pyo3(signature = (strings, unit_map, target_mult, target_offset, on_error_mode, require_tag, fallback_unit_key))]
fn fast_fused_normalize(
    _py: Python<'_>,
    strings: &Bound<'_, PyList>,
    unit_map: HashMap<String, UnitMetadata>, 
    target_mult: f64,
    target_offset: f64,
    on_error_mode: u8, // 0: raise, 1: coerce, 2: clip
    require_tag: bool,
    fallback_unit_key: &str, // Unit default jika string angka murni
) -> PyResult<Vec<f64>> {
    
    let len = strings.len();
    let mut results: Vec<f64> = Vec::with_capacity(len); // Mencegah realokasi memori array!
    
    for (i, item) in strings.iter().enumerate() {
        if let Ok(rust_str) = item.extract::<&str>() {
            let (raw_val, unit_opt) = parse_physical_string(rust_str);
            
            if raw_val.is_nan() {
                let t = rust_str.trim();
                if on_error_mode == 0 && !t.is_empty() && !t.eq_ignore_ascii_case("nan") && !t.eq_ignore_ascii_case("none") {
                    return Err(PyValueError::new_err(format!("PARSE_ERROR|{}", i)));
                }
                results.push(f64::NAN);
                continue;
            }

            // 🌟 KUNCI PERBAIKAN: Resolusi Unit dengan fallback
            let u_key = match unit_opt {
                Some(u) => u,
                None => {
                    if require_tag {
                        if on_error_mode == 0 {
                            return Err(PyValueError::new_err(format!("MISSING_UNIT_TAG|{}", i)));
                        } else {
                            results.push(f64::NAN);
                            continue;
                        }
                    } else {
                        fallback_unit_key // Gunakan unit dari parameter source_unit Python!
                    }
                }
            };

            // Proses Lookup HashMap dan Perhitungan Fisika
            if let Some(&(multiplier, offset, axiom_min, axiom_max)) = unit_map.get(u_key) {
                let mut val = raw_val;

                if let Some(min) = axiom_min {
                    if val < min {
                        if on_error_mode == 0 {
                            return Err(PyValueError::new_err(format!("AXIOM_MIN|{}|{}|{}", i, val, min)));
                        } else if on_error_mode == 2 {
                            val = min;
                        } else {
                            results.push(f64::NAN); continue;
                        }
                    }
                }

                if let Some(max) = axiom_max {
                    if val > max {
                        if on_error_mode == 0 {
                            return Err(PyValueError::new_err(format!("AXIOM_MAX|{}|{}|{}", i, val, max)));
                        } else if on_error_mode == 2 {
                            val = max;
                        } else {
                            results.push(f64::NAN); continue;
                        }
                    }
                }

                // Kalkulasi Cepat JIT Scaling
                let base_val = (val + offset) * multiplier;
                let target_val = (base_val / target_mult) - target_offset;
                results.push(target_val);
            } else {
                if on_error_mode == 0 {
                    return Err(PyValueError::new_err(format!("UNIT_ERROR|{}|{}", i, u_key)));
                } else {
                    results.push(f64::NAN);
                }
            }
        } else {
            results.push(f64::NAN); // Tipe data aneh (bukan string)
        }
    }

    Ok(results)
}

#[pymodule]
fn _rust_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fast_fused_normalize, m)?)?;
    Ok(())
}