---
seo_type: TechArticle
title: "Physics-Informed Loss Tribunals"
description: "Physics-informed loss functions for Sci-ML. Enforce physical bounds via ReLU penalties, and validate PDE equilibrium via SI DNA residual inspection."
keywords: "physics-informed loss function pytorch, enforce physical bounds neural network, PDE equilibrium loss python, penalize impossible physics AI"
---

# Physics-Informed Loss Functions

Standard Deep Learning operates on a simple principle: evaluate the numerical distance between a prediction and a target using functions like Mean Squared Error (MSE), then backpropagate the error. 

However, in Scientific Machine Learning (SciML), standard neural networks are mathematically blind. A standard `nn.Linear` layer does not know if it is predicting absolute temperature, mass, or velocity. If an untrained neural network predicts a mass of `-50.0 kg`, standard MSE simply sees a number. 

Phaethon bridges this gap using **Physics-Informed Loss Functions**. Instead of relying solely on data, Phaethon utilizes `AxiomLoss` to enforce strict natural boundaries and `ResidualLoss` to enforce dynamic differential equations across the continuous domain.

---

## The "Crash vs. Learn" Paradigm

A common question in SciML architecture is: *Why does `PTensor` allow the creation of negative mass without crashing, only to penalize it later in the Loss Function?*

If `PTensor` immediately threw a `ValueError` the moment a neural network predicted `-5.0 kg`, the training script would crash at Epoch 0. The neural network would never have the opportunity to execute `loss.backward()` to learn from its mistake. 

By allowing the mathematically invalid number to pass through the forward pass, Phaethon hands the impossible tensor over to the **Loss Tribunals**. These loss functions translate the physical violation into a massive mathematical penalty gradient. When PyTorch backpropagates this penalty, the optimizer is forced to aggressively correct its weights, teaching the AI to respect the laws of physics.

---

## AxiomLoss: The Absolute Law Tribunal

`AxiomLoss` acts as the constitution of your physical simulation. It is entirely blind to the specific dynamics (like fluid flow or heat transfer) and only cares about absolute natural laws: Mass cannot be negative, and Kelvin cannot drop below zero.

### API Reference

```python
phaethon.pinns.AxiomLoss(
    expected_dimension: str, 
    min_val: float | None = None, 
    max_val: float | None = None
)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">expected_dimension</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">The specific physical dimension this tribunal is built to judge (e.g., 'mass', 'pressure'). This acts as a strict architectural guardrail to prevent developers from accidentally passing the wrong physical tensor into the wrong loss function.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">min_val / max_val</span>
    <span class="p-sep">—</span>
    <span class="p-type">float | None</span>
  </div>
  <div class="p-desc">Manual overrides for engineering bounds. If left as None, the loss function automatically extracts the fundamental SI laws from Phaethon's unit registry.</div>
</div>

### Mechanism of Action
`AxiomLoss` utilizes a differentiable `torch.relu` mechanism. If a predicted value falls outside the allowed minimum or maximum bounds, the ReLU activation returns the exact magnitude of the violation, which is then summed and backpropagated as a severe penalty.

### Example: Guiding a Blind Neural Network

In this example, we initialize a neural network with a massive negative bias. The AI will initially predict highly negative mass. `AxiomLoss` will catch this and force the AI to correct itself over multiple epochs.

```python
import torch
import torch.nn as nn
import phaethon.pinns as pnn
import phaethon.units as u

class MassPredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Linear(1, 1)
        # Force it to predict heavily negative numbers initially
        nn.init.constant_(self.net.bias, -10.0) 

    def forward(self, t_phys):
        # 1. Strip physics for the raw neural network
        t_raw = pnn.assemble(t_phys)
        
        # 2. AI predicts a raw, dimension-less float (e.g., -10.5)
        m_raw = self.net(t_raw)
        
        # 3. Wrap the raw float in physical DNA
        return pnn.PTensor(m_raw, unit=u.Kilogram)

# Setup Training
model = MassPredictor()
optimizer = torch.optim.Adam(model.parameters(), lr=0.1)
axiom_tribunal = pnn.AxiomLoss(expected_dimension='mass')

# Input data
time_input = pnn.PTensor([[1.0], [2.0], [3.0]], unit=u.Second)

for epoch in range(100):
    optimizer.zero_grad()
    
    # Forward Pass
    mass_pred = model(time_input)
    
    # AxiomLoss reads u.Kilogram's inherent rule (min = 0.0) 
    # and severely penalizes the negative predictions.
    loss = axiom_tribunal(mass_pred)
    
    loss.backward()
    optimizer.step()
```

### Manual Engineering Bounds
While fundamental units have predefined laws, engineering applications often require operational bounds. For example, if you are simulating liquid water, the temperature must stay between 0 Celsius and 100 Celsius. You can override the fundamental laws using `min_val` and `max_val`.

```python
# The AI will be heavily penalized if the prediction drops below 273.15 K 
# or exceeds 373.15 K.
water_state_tribunal = pnn.AxiomLoss(
    expected_dimension='temperature', 
    min_val=273.15, 
    max_val=373.15
)
```

---

## ResidualLoss: The Dynamics Validator

While `AxiomLoss` checks absolute bounds, `ResidualLoss` evaluates whether a prediction makes sense according to a Partial Differential Equation (PDE), such as the Navier-Stokes or Burgers' equation.

In PINNs, developers scatter thousands of "Collocation Points" (randomized sensors) across the continuous spatial and temporal domain. At each point, the neural network guesses the state of the system. `ResidualLoss` calculates the physical gradients at those points and checks if they balance out according to the PDE.

### API Reference

```python
phaethon.pinns.ResidualLoss()
```

The forward pass of `ResidualLoss` requires two arguments:

1. `residual`: The computed physical tensor from your differential equation.
2. `target`: The equilibrium state (defaults to `0.0`).

### The Equation Balance Guardrail

Standard PyTorch MSE allows you to calculate the difference between any two tensors. If a developer accidentally compares a residual representing Acceleration with a target representing Speed, PyTorch will silently compute the math. The model will converge, but it will learn a completely broken universe.

Phaethon's `ResidualLoss` acts as a strict fail-safe. Before calculating the Mean Squared Error, it forensically inspects the SI DNA of both the `residual` and the `target`. If they do not match, training is halted immediately.

```text
EquationBalanceError: The PDE residual and target state do not share the same physical dimension.
  Residual : acceleration [m/s2]
  Target   : speed [m/s]
```

### Example: Evaluating Equilibrium

Most physics equations are evaluated by moving all terms to one side, meaning the equation must sum to zero (Equilibrium).

```python
import phaethon.pinns as pnn
import phaethon.units as u

pde_tribunal = pnn.ResidualLoss()

# Assume we have computed spatial and temporal derivatives
# du_dt (Acceleration) and du_dx (Frequency)
du_dt = pnn.PTensor([5.0], unit=u.MeterPerSecondSquared, requires_grad=True)
u_pred = pnn.PTensor([2.0], unit=u.MeterPerSecond, requires_grad=True)
du_dx = pnn.PTensor([2.5], unit=u.Rate, requires_grad=True)

# Calculate the PDE residual
# u_pred * du_dx synthesizes to Acceleration (m/s2), allowing safe addition.
residual = du_dt + (u_pred * du_dx)

# Target defaults to 0.0, forcing the AI to adjust weights 
# until the residual reaches equilibrium.
loss_pde = pde_tribunal(residual, target=0.0)

loss_pde.backward()
```

By leveraging `AxiomLoss` for absolute boundaries and `ResidualLoss` for dynamic equation balancing, Phaethon ensures that your neural networks converge accurately and strictly within the confines of physical reality.