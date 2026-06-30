> **UNTRUSTED — DO NOT USE AS A DATA SOURCE.** Corrupted first-run output, retained for provenance only. See _README_UNTRUSTED.md.

Below is a **revised, clearer Markdown deliverable** designed for **admins and leadership who did NOT participate in the analysis**.

The goal is to make it easy to understand:

* ✅ What each vendor does
* ✅ What the listed items actually are (software vs tools vs SDKs)
* ✅ Whether they are relevant to Windows systems
* ✅ Where Linux/Unix relevance exists

***

# 📄 Vendor and Software Summary (Operational View)

## 🎯 Purpose

This document provides a **simplified, readable summary** of:

* Vendors reviewed in this analysis
* Known software or tools associated with those vendors
* Whether the software is relevant to:
  * Windows systems ✅
  * Linux/Unix systems ⚠️
  * Or not applicable ❌

This list is intended to help administrators quickly recognize:

* Software that may be installed on endpoints
* Tools used by users or engineering teams
* SDKs or supporting libraries embedded in other applications

***

# ✅ Vendors With Direct Windows Software (Primary Focus)

These vendors produce **software that may be installed on Windows workstations or servers**.

***

## 🟢 Qihoo 360 (Endpoint Security Vendor)

**What they do:**  
Consumer and enterprise security software (antivirus, system tools)

**Software:**

* 360 Total Security → Endpoint security / antivirus
* 360 Safe Guard → Security and optimization suite
* 360 Browser → Web browser

✅ **Windows relevance:** YES (installed on endpoints)  
⚠️ **Linux relevance:** NO

***

## 🟢 Hikvision (Video Surveillance Vendor)

**What they do:**  
Camera systems and video surveillance platforms

**Software:**

* HikCentral Professional → Video management system (server platform)
* iVMS-4200 → Desktop client for viewing/controlling cameras
* SADP Tool → Device discovery utility
* Hikvision SDK → Developer libraries used in integrations

✅ **Windows relevance:** YES (client + server installs)  
⚠️ **Linux relevance:** YES (server deployments in some environments)

📌 **Important:**  
SDK components may exist inside third-party applications.

***

## 🟢 Dahua (Video Surveillance Vendor)

**What they do:**  
Security cameras and video management systems

**Software:**

* SmartPSS → Desktop client for surveillance systems
* DSS Express → Server-based video management
* ConfigTool → Device configuration utility
* Dahua SDK → Integration libraries

✅ **Windows relevance:** YES  
⚠️ **Linux relevance:** YES (server-side components)

📌 Similar profile to Hikvision

***

## 🟢 Huawei (Enterprise / Device / Network Vendor)

**What they do:**  
Telecom, networking, enterprise IT platforms

**Software:**

* HiSuite → Desktop tool for managing Huawei devices
* eSight → Network management platform
* iMaster NCE → Software-defined networking platform
* ManageOne → Cloud management platform
* FusionCompute → Virtualization platform
* Cloud Stack → Private cloud platform

✅ **Windows relevance:** YES (HiSuite, some tools)  
⚠️ **Linux relevance:** YES (most enterprise platforms deployed on Linux)

📌 Most Huawei enterprise software is **NOT endpoint-installed** but server-based.

***

## 🟢 Tencent (Consumer Software Vendor)

**What they do:**  
Messaging, communication, and cloud services

**Software:**

* QQ → Messaging client
* WeChat Desktop → Desktop messaging application
* Tencent Meeting (VooV) → Video conferencing
* Tencent Cloud SDK → Developer libraries

✅ **Windows relevance:** YES (very common user-installed apps)  
⚠️ **Linux relevance:** LIMITED

📌 Common in user environments

***

## 🟢 TP-Link (Networking Vendor)

**What they do:**  
Network devices (routers, switches, wireless systems)

**Software:**

* Omada Controller → Centralized network management software
* TP-Link Tether → Device management interface (primarily mobile, but ecosystem-related)

✅ **Windows relevance:** YES (controller software)  
⚠️ **Linux relevance:** YES (controller often runs on Linux servers)

***

## 🟢 DJI (Drone / Device Vendor)

**What they do:**  
Drones and control systems

**Software:**

* DJI Assistant 2 → Device configuration and firmware management
* DJI GO 4 → Legacy ecosystem control software
* DJI Fly → Ecosystem interaction
* DJI SDK → Developer tools for drone integration

✅ **Windows relevance:** YES (management tools)  
⚠️ **Linux relevance:** LIMITED

📌 SDK may appear embedded in third-party systems

***

# ⚠️ Vendors With Limited or Specialized Software

These vendors may have **software in limited or specialized environments** (not common on typical user systems).

***

## 🟡 NetPosa (Surveillance Analytics Vendor)

**What they do:**  
Video analysis and surveillance platforms

**Software:**

* NetPosa Video Platform → Surveillance system software

✅ **Windows relevance:** YES (limited deployments)  
⚠️ **Linux relevance:** YES (likely primary deployment method)

***

## 🟡 Inspur (Server / Infrastructure Vendor)

**What they do:**  
Servers, data center systems, HPC

**Software:**

* Server Management Software → Hardware management tools
* Cluster Management System → HPC/cluster orchestration

✅ **Windows relevance:** LIMITED  
⚠️ **Linux relevance:** YES (primary environment)

***

## 🟡 BGI / MGI (Genomics / Lab Software)

**What they do:**  
DNA sequencing and bioinformatics

**Software:**

* Sequencer Control Software → Controls lab equipment
* Bioinformatics Platform → Data analysis

✅ **Windows relevance:** LIMITED (lab computers only)  
⚠️ **Linux relevance:** HIGH (data processing environments)

📌 Typically NOT present outside research environments

***

## 🟡 BOE Technology (Hardware / Display Vendor)

**What they do:**  
Display panels (screens)

**Software:**

* Display Driver Software → Hardware driver

✅ **Windows relevance:** YES (driver-level only)  
⚠️ **Linux relevance:** POSSIBLE (driver/firmware support)

📌 Typically hidden within system drivers

***

# ❌ Vendors With No Relevant Windows Software

These vendors were evaluated and determined to have **no meaningful Windows software presence**.

***

## ❌ AI / Analytics Platforms

* SenseTime
* Yitu
* CloudWalk

📌 Backend systems, not endpoint software

***

## ❌ Biotech / CRO

* WuXi AppTec

📌 Internal or SaaS-based systems only

***

## ❌ Telecom / Infrastructure

* Baicells

📌 Hardware and network infrastructure only

***

## ❌ Hardware / Components

* Tianma Microelectronics
* Innolight

📌 Embedded components (no installable software)

***

## ❌ Industrial / Energy / Aerospace / Logistics

* AVIC
* CASIC
* COMAC
* China SpaceSat
* CNNC
* CGN
* CNOOC
* China Three Gorges
* COSCO Shipping
* Sinotrans
* CSCEC
* Norinco
* CATL
* BYD
* ChemChina
* CNCEC

📌 Industrial systems, not endpoint software

***

# ✅ Key Takeaways

### 1. Small Number of Relevant Vendors

Only a **limited set of vendors produce software that appears on Windows systems**

***

### 2. Most Risk Comes From:

* Surveillance software (Hikvision, Dahua)
* Consumer/endpoint apps (Tencent, Qihoo)
* Device tools (DJI, Huawei tools)

***

### 3. Many Entities Are NOT Relevant for Endpoint Detection

* AI platforms
* Industrial systems
* Infrastructure vendors

***

### 4. Linux/Unix Context Matters

* Many enterprise products (Huawei, Inspur, NetPosa)  
  are **primarily deployed on Linux systems**

***

# ✅ How To Use This List

This list is intended for:

* ✅ Quick recognition of installed software
* ✅ Identifying potential exposure on endpoints
* ✅ Supporting conversations with system owners
* ✅ Initial triage before deeper indicator searches

***

