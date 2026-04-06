"""
Currency and Financial Dimension Module.

Unlike strictly physical dimensions, currencies are highly volatile.
This module uses contextual scaling (@axiom.scale) alongside a smart FX resolver 
to allow users to inject real-time exchange rates at runtime.

The absolute base unit (Anchor) for this dimension is the US Dollar (USD).
All cross-currency conversions (e.g., EUR to JPY) are mathematically routed 
through the USD anchor automatically.
"""
from ..base import BaseUnit
from .. import axioms as _axiom
from ..axioms import CtxProxy
from ..compat import ContextDict

def fx_rate(symbol: str, default: float) -> CtxProxy:
    """
    Smart exchange rate resolver utilizing the native CtxProxy.
    It dynamically checks the runtime context for either direct quotes (e.g., 'eur_to_usd') 
    or inverse quotes (e.g., 'usd_to_eur') and applies the correct mathematical inversion
    without breaking derived unit propagation (e.g., price_per_mass).
    """
    symbol = symbol.lower()
    direct_key = f"{symbol}_to_usd"
    inverse_key = f"usd_to_{symbol}"

    def _evaluator(ctx: ContextDict) -> float:
        if direct_key in ctx:
            return float(ctx[direct_key])
        if inverse_key in ctx:
            val = float(ctx[inverse_key])
            if val == 0:
                raise ValueError(f"Exchange rate for {inverse_key} cannot be zero.")
            return 1.0 / val
        return default
        
    return CtxProxy(_evaluator=_evaluator)

@_axiom.bound(abstract=True)
class Currency(BaseUnit):
    """
    The primary parent class for Financial dimensions.
    The absolute base unit is the US Dollar (USD).
    """
    dimension = "currency"

# =========================================================================
# 1. THE RESERVE CURRENCY (Anchor: USD)
# =========================================================================

class USDollar(Currency):
    """
    The absolute anchor of Phaethon's Currency dimension.
    
    Base Multiplier: 1.0 (Reference point for all financial conversions).
    """
    symbol = "USD"
    aliases = ["$", "usd", "us dollar", "us dollars", "bucks", "us$"]
    base_multiplier = 1.0

# =========================================================================
# 2. MAJOR FIAT CURRENCIES (G10 & Global Giants)
# =========================================================================

@_axiom.scale(formula=fx_rate("eur", default=1.16))
class Euro(Currency):
    """
    European Union Euro.
    Anchor Unit: US Dollar (USD).
    
    To override the default rate, inject 'eur_to_usd' or 'usd_to_eur' via context.
    """
    symbol = "EUR"
    aliases = ["€", "eur", "euro", "euros"]
    base_multiplier = 1.0

@_axiom.scale(formula=fx_rate("gbp", default=1.26))
class BritishPound(Currency):
    """
    British Pound Sterling.
    Anchor Unit: US Dollar (USD).
    
    To override the default rate, inject 'gbp_to_usd' or 'usd_to_gbp' via context.
    """
    symbol = "GBP"
    aliases = ["£", "gbp", "pound", "pounds", "quid", "sterling"]
    base_multiplier = 1.0

@_axiom.scale(formula=fx_rate("jpy", default=0.0067))
class JapaneseYen(Currency):
    """
    Japanese Yen.
    Anchor Unit: US Dollar (USD).
    
    To override the default rate, inject 'jpy_to_usd' or 'usd_to_jpy' via context.
    """
    symbol = "JPY"
    aliases = ["¥", "jpy", "yen"]
    base_multiplier = 1.0

@_axiom.scale(formula=fx_rate("chf", default=1.12))
class SwissFranc(Currency):
    """
    Swiss Franc.
    Anchor Unit: US Dollar (USD).
    
    To override the default rate, inject 'chf_to_usd' or 'usd_to_chf' via context.
    """
    symbol = "CHF"
    aliases = ["chf", "swiss franc", "francs", "swiss francs"]
    base_multiplier = 1.0

@_axiom.scale(formula=fx_rate("cad", default=0.74))
class CanadianDollar(Currency):
    """
    Canadian Dollar.
    Anchor Unit: US Dollar (USD).
    
    To override the default rate, inject 'cad_to_usd' or 'usd_to_cad' via context.
    """
    symbol = "CAD"
    aliases = ["cad", "canadian dollar", "c$", "loonie"]
    base_multiplier = 1.0

@_axiom.scale(formula=fx_rate("aud", default=0.65))
class AustralianDollar(Currency):
    """
    Australian Dollar.
    Anchor Unit: US Dollar (USD).
    
    To override the default rate, inject 'aud_to_usd' or 'usd_to_aud' via context.
    """
    symbol = "AUD"
    aliases = ["aud", "australian dollar", "a$", "dollarydoos"]
    base_multiplier = 1.0

@_axiom.scale(formula=fx_rate("cny", default=0.14))
class ChineseYuan(Currency):
    """
    Chinese Yuan Renminbi.
    Anchor Unit: US Dollar (USD).
    
    To override the default rate, inject 'cny_to_usd' or 'usd_to_cny' via context.
    """
    symbol = "CNY"
    aliases = ["cny", "rmb", "yuan", "renminbi", "kuai"]
    base_multiplier = 1.0

# =========================================================================
# 3. EMERGING MARKETS & ASIAN HUBS
# =========================================================================

@_axiom.scale(formula=fx_rate("sgd", default=0.74))
class SingaporeDollar(Currency):
    """
    Singapore Dollar.
    Anchor Unit: US Dollar (USD).
    
    To override the default rate, inject 'sgd_to_usd' or 'usd_to_sgd' via context.
    """
    symbol = "SGD"
    aliases = ["sgd", "singapore dollar", "s$"]
    base_multiplier = 1.0

@_axiom.scale(formula=fx_rate("inr", default=0.012))
class IndianRupee(Currency):
    """
    Indian Rupee.
    Anchor Unit: US Dollar (USD).
    
    To override the default rate, inject 'inr_to_usd' or 'usd_to_inr' via context.
    """
    symbol = "INR"
    aliases = ["inr", "₹", "rupee", "rupees"]
    base_multiplier = 1.0

@_axiom.scale(formula=fx_rate("idr", default=0.000059))
class IndonesianRupiah(Currency):
    """
    Indonesian Rupiah.
    Anchor Unit: US Dollar (USD).
    
    To override the default rate, inject 'idr_to_usd' or 'usd_to_idr' via context.
    """
    symbol = "IDR"
    aliases = ["idr", "Rp", "rp", "rupiah", "perak"]
    base_multiplier = 1.0

# =========================================================================
# 4. CRYPTOCURRENCY (Digital & Volatile)
# =========================================================================

@_axiom.scale(formula=fx_rate("btc", default=65000.0))
class Bitcoin(Currency):
    """
    Bitcoin (BTC).
    Anchor Unit: US Dollar (USD).
    
    To override the default rate, inject 'btc_to_usd' or 'usd_to_btc' via context.
    """
    symbol = "BTC"
    aliases = ["₿", "btc", "bitcoin", "bitcoins", "sats"]
    base_multiplier = 1.0

@_axiom.scale(formula=fx_rate("eth", default=3500.0))
class Ethereum(Currency):
    """
    Ethereum (ETH).
    Anchor Unit: US Dollar (USD).
    
    To override the default rate, inject 'eth_to_usd' or 'usd_to_eth' via context.
    """
    symbol = "ETH"
    aliases = ["eth", "ethereum", "ether", "gwei"]
    base_multiplier = 1.0

@_axiom.scale(formula=fx_rate("sol", default=150.0))
class Solana(Currency):
    """
    Solana (SOL).
    Anchor Unit: US Dollar (USD).
    
    To override the default rate, inject 'sol_to_usd' or 'usd_to_sol' via context.
    """
    symbol = "SOL"
    aliases = ["sol", "solana"]
    base_multiplier = 1.0

@_axiom.scale(formula=fx_rate("usdt", default=1.0))
class Tether(Currency):
    """
    Tether Stablecoin (USDT).
    Anchor Unit: US Dollar (USD).
    
    To override the default rate (if depegged), inject 'usdt_to_usd' or 'usd_to_usdt' via context.
    """
    symbol = "USDT"
    aliases = ["usdt", "tether", "usd_tether"]
    base_multiplier = 1.0

@_axiom.scale(formula=fx_rate("usdc", default=1.0))
class USDCoin(Currency):
    """
    USD Coin (USDC).
    Anchor Unit: US Dollar (USD).
    
    To override the default rate (if depegged), inject 'usdc_to_usd' or 'usd_to_usdc' via context.
    """
    symbol = "USDC"
    aliases = ["usdc", "usd coin"]
    base_multiplier = 1.0