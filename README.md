# Pharma++
PharmaCare+ is a secure, multi-tenant SaaS pharmacy management system built with Flask &amp; MySQL. It features data isolation, automated inventory alerts, a sleek glassmorphism UI, and Pandas-powered bulk CSV data uploads for pharmacy owners.

# 💊 Pharma++ 
**Next-Generation Multi-Tenant SaaS Pharmacy Management System**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey?style=for-the-badge&logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange?style=for-the-badge&logo=mysql)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.0-purple?style=for-the-badge&logo=bootstrap)

> **Pharma++** is a highly secure, data-driven, and scalable SaaS (Software as a Service) application designed to revolutionize how independent pharmacies manage their operations. Built with a robust Flask backend and a dynamic Glassmorphism frontend, it offers enterprise-grade features including multi-tenant data isolation, automated analytics, and lightning-fast bulk data processing.

---

## ✨ The "Wow" Features

### 🔒 True Multi-Tenant Architecture
Pharma++ is built for scale. Unlike traditional single-user applications, it utilizes a sophisticated `owner_id` relational mapping system. This ensures **absolute data isolation**—multiple pharmacy owners can use the same application simultaneously, securely accessing only their private workspace, inventory, and sales data.

### ⚡ Pandas-Powered Bulk Data Injection
Say goodbye to manual data entry. Integrated with the **Python Pandas** library, Pharma++ allows administrators to seamlessly upload thousands of records (Medicines, Suppliers, Customers, and Delivery Agents) in seconds using `.csv` files. The system intelligently handles data cleaning and automatically updates the database.

### 📊 Smart Command-Center Dashboard
A visually stunning, **Glassmorphism-inspired UI** that provides a real-time pulse on your business. Instantly track:
* Total active medicines and current stock levels.
* Total registered suppliers and returning customers.
* **Estimated Inventory Net Worth** calculated dynamically.

### 🚨 Automated Intelligence & Alerts
* **Low Stock Radar:** Automatically flags inventory dropping below the critical threshold (50 units), ensuring you never run out of best-sellers.
* **Expiry Vanguard:** Scans the entire database to detect and alert you about medicines expiring within the next 60 days, minimizing loss and ensuring compliance.

### 💸 End-to-End Sales & Logistics Tracking
A dedicated module to log point-of-sale transactions, track total revenue generated, identify your top 5 best-selling medicines, and manage registered delivery personnel for home deliveries.

---

## 🛠️ Technology Stack

**Backend Engine**
* **Language:** Python 3
* **Framework:** Flask
* **Data Processing:** Pandas
* **Authentication:** Secure Flask Session Management

**Database Layer**
* **RDBMS:** MySQL
* **Connector:** `mysql-connector-python`
* **Architecture:** Relational Schema with Foreign Key Constraints & Triggers

**Frontend Interface**
* **Core:** HTML5, CSS3, JavaScript
* **Framework:** Bootstrap 5
* **Design Language:** Modern Glassmorphism (Frosted Glass UI)

---

## 🏗️ Database Schema Overview

Pharma++ operates on a strictly normalized MySQL database with the following core entities:
* `users`: Handles authentication and multi-tenant mapping.
* `medicine`: Tracks nomenclature, stock, pricing, and expiry.
* `supplier`: Manages vendor logistics and contacts.
* `customer` & `customer_audit`: Logs buyer details and auto-records data entry actions.
* `deliveryperson`: Manages fleet and vehicle registrations.
* `orders` & `order_medicine`: Relational tables for tracking complex multi-item sales and revenue.

---

