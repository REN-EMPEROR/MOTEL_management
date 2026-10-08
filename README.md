# 🏨 GrandStay — Luxury Hotel & Motel Management System

A modern, high-contrast, luxury-inspired web application for hotel and motel management. Designed with a luxury hospitality aesthetic (inspired by modern SaaS and boutique hotel booking engines), featuring real-time floor heatmaps, 7-day occupancy Gantt scheduling, high-fidelity room cataloging, split-view reservation flows, and printable guest folio invoices.

---

## ✨ Features

- **Executive Analytics Dashboard**:
  - Live KPI metric cards with SVG sparkline trend charts (Occupancy Rate, RevPAR Yield, Total Bookings, Front Desk activity).
  - 2D **Floor Heatmap Matrix** with real-time status glowing dots (`Available`, `Occupied`, `Cleaning`, `Maintenance`).
  - Rolling **7-Day Occupancy Gantt Timeline** showing multi-day stay blocks and guest schedules.
- **Rooms Catalog & Inventory**:
  - Dual-view switcher: **High-Fidelity Cards Grid** with photography & glowing indicators vs. **Compact Table View**.
  - Quick operational status switcher (`Available`, `Occupied`, `Cleaning`, `Maintenance`).
  - Modal drawers for adding new rooms and editing room parameters.
- **Reservations & Guest Logs**:
  - Guest registry with formatted contact details and pastel avatar initials.
  - Live client-side instant search across guest names, phone numbers, and room numbers.
  - Quick-filter tabs (`All`, `Active / Booked`, `Checked Out`).
  - Instant checkout workflow with automatic room availability return.
- **Reservation Desk**:
  - Luxury split-screen booking interface.
  - Real-time stay duration and fee breakdown calculation.
- **Guest Folio & Invoicing**:
  - Luxury boutique hotel folio layout with itemized accommodation charges and amenities.
  - Dedicated `@media print` layout optimized for browser printing and saving clean PDF invoices.
- **Design System & Micro-Interactions**:
  - Light mode (crisp off-white `#F8F9FA`) and Dark mode (deep slate `#0B0F17` / `#151C28`) with persistent theme switcher.
  - Editorial typography (`Playfair Display`) paired with clean modern grotesk (`Plus Jakarta Sans`).
  - Smooth transitions, glassmorphic floating navigation, and pulsing status rings.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite 3 (`hotel.db`, auto-initialized on first launch)
- **Frontend**: HTML5, Tailwind CSS, Custom Modern CSS Design System, Vanilla JavaScript
- **Typography**: Google Fonts (*Playfair Display* & *Plus Jakarta Sans*)

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ installed

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/REN-EMPEROR/MOTEL_management.git
cd MOTEL_management
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
The database and demo inventory will be initialized automatically on the first launch.
