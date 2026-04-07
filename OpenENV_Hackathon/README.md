---
title: OpenEnv Email Triage
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
sdk_version: 6.11.0

---

# 📧 Email Triage Agent (OpenEnv)

An interactive AI environment that simulates **real-world enterprise email triage**.

---

## 🧠 What This System Does

This project models how companies handle incoming emails by:

- 📩 Classifying emails (billing, technical, sales, etc.)
- ⚡ Assigning priority based on SLA urgency
- 🔀 Routing emails to the correct team
- 🎯 Evaluating decisions using a reward system

---

## 🚀 Key Features

- ✅ Multi-step decision environment  
- ✅ SLA-aware prioritization  
- ✅ Queue-based email handling  
- ✅ Reward-driven evaluation  
- ✅ Interactive Gradio UI (live demo)  

---

## 🎮 How to Use (Demo)

1. Select a task:
   - `easy` → basic classification  
   - `medium` → queue + SLA decisions  
   - `hard` → multi-step + strict constraints  

2. Click **🔄 Reset Environment**

3. Choose:
   - Category  
   - Priority  
   - Assign To  

4. Click **🚀 Submit Action**

5. Observe:
   - Reward score  
   - Next email  
   - System behavior  

---

## ⚡ Quick Demo

Use built-in buttons:

- ✅ **Correct Decision** → optimal handling (high reward)  
- ❌ **Wrong Decision** → poor handling (low/negative reward)  

---

## 🏗️ Environment Design

### Observation
The agent receives:
- Current email  
- Queue length  
- Active SLA pressure  
- Previous actions  

---

### Action Format

```json
{
  "category": "billing | technical | sales | spam | other",
  "priority": "low | medium | high | urgent",
  "assign_to": "support | engineering | sales | ignore",
  "draft_reply": "optional (used in hard task)"
}