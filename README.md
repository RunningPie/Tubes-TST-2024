### README.md untuk Proyek Tugas Besar TST

---

# 📘 TaskHub - Sistem Manajemen Proyek Akademik
**Dibuat oleh:** Dama Dhananjaya Daliman (18222047)  
Proyek ini merupakan solusi manajemen proyek akademik yang memanfaatkan teknologi AI, fuzzy logic, dan integrasi layanan modern. 

Bisa diakses di:
- **Frontend Deployment:** [TaskHub Frontend](https://taskhub-tst.vercel.app/)  
- **Backend Deployment:** [TaskHub Backend](https://tubes-tst-2024-production.up.railway.app/)  

Laporan pengembangan dan dokumentasinya bisa diakses di:
- **GDocs Laporan:** [TaskHub Report](https://docs.google.com/document/d/1uDZXZT3-4li0obyQDzyl-8Is3cpIAbl2/edit?usp=sharing&ouid=116101569598927163108&rtpof=true&sd=true)  

---

## 📑 Daftar Isi  
1. [Business Capability Model](#-1-business-capability-model)  
2. [Dekomposisi Subdomain](#-2-dekomposisi-subdomain)  
3. [Fungsi Subdomain](#-3-fungsi-subdomain)  
4. [Arsitektur dan Model Proses](#-4-arsitektur-dan-model-proses)  
5. [Teknologi yang Digunakan](#-5-teknologi-yang-digunakan)  
6. [Flow Pengembangan](#-6-flow-pengembangan)
-- 🔽🔽 SPEK WAJIB 🔽🔽 --
7. **[Fitur Utama: Fuzzy Rule Based System (FRBS)](#-7-fitur-utama-fuzzy-rule-based-system-frbs)**
8. **[Kontainerisasi](#-8-kontainerisasi)**  
9. **[Autentikasi Pengguna (Manusia)](#-9-autentikasi-pengguna-manusia) ** 
10. **[Autentikasi API](#-10-autentikasi-api)  **
11. **[Dokumentasi API](#-11-dokumentasi-api)  **
12. **[Integrasi dengan Layanan Lain](#-12-integrasi-dengan-layanan-lain) ** 

---

## 📊 **1. Business Capability Model**  
Model ini mencakup kapabilitas bisnis utama TaskHub, mulai dari manajemen jadwal, alokasi tugas, hingga rekomendasi berbasis AI.  

![Business Capability Model](https://github.com/RunningPie/Tubes-TST-2024/blob/main/docs/supporting_images/BCM.png)

---

## 🧩 **2. Dekomposisi Subdomain**  
TaskHub berfokus pada subdomain unik yaitu **Academic Project Management** yang mendukung kolaborasi dan manajemen proyek dengan AI.  

![Dekomposisi Subdomain](https://github.com/RunningPie/Tubes-TST-2024/blob/main/docs/supporting_images/Dekomposisi_Subdomain.png)

---

## 🛠 **3. Fungsi Subdomain**  
TaskHub terdiri dari:  
- **Core Subdomain:** AI-supported Task Allocation, Task Tracking, dan lainnya.  
- **Generic Subdomain:** Cloud Storage, Authentication, dll.  
- **Supporting Subdomain:** Helpbot, Customizable Templates, dll.  

![Pemetaan Subdomain](https://github.com/RunningPie/Tubes-TST-2024/blob/main/docs/supporting_images/Pemetaan_Subdomain.png)

---

## 🏛 **4. Arsitektur dan Model Proses**  
Sistem berbasis **layered architecture** dengan tiga lapisan utama: Infrastruktur, Logika Bisnis, dan Presentasi.  

![Arsitektur Sistem](https://github.com/RunningPie/Tubes-TST-2024/blob/main/docs/supporting_images/Arsitektur.png)

---

## 🔄 **5. Teknologi yang Digunakan**  
- **Backend:** Python + FastAPI  
- **Frontend:** Vanilla HTML, CSS, JS  
- **AI Engine:** Fuzzy Rule Based System (dikembangkan dengan Python)  
- **Database:** PostgreSQL (Supabase)  
- **Autentikasi:** Supabase  

---

## 📅 **6. Flow Pengembangan**  
Tahapan pengembangan dimulai dari setup lingkungan hingga deployment ke Vercel.  

![Flow Pengembangan](https://github.com/RunningPie/Tubes-TST-2024/blob/main/docs/supporting_images/Flow_Pengembangan.png)

---

## 🚀 **7. Fitur Utama: Fuzzy Rule Based System (FRBS)**  
Fitur utama menggunakan fuzzy logic untuk alokasi dan pelacakan tugas:  
- **Fuzzification:** Menentukan nilai derajat keanggotaan.  
- **Defuzzification:** Menghasilkan output akhir berbasis aturan fuzzy.  

Kode implementasi tersedia di [repository GitHub](https://github.com/RunningPie/Tubes-TST-2024).

---

## 📦 **8. Kontainerisasi**  
Layanan backend dikontainerisasi menggunakan Docker untuk mempermudah deployment.

[>> Cek Dockerfile <<](https://github.com/RunningPie/Tubes-TST-2024/blob/main/backend/dockerfile)

---

## 🔑 **9. Autentikasi Pengguna (Manusia)**  
Autentikasi berbasis Supabase dengan opsi login tradisional dan OAuth (GitHub, Google).  

---

## 🔐 **10. Autentikasi API**  
Validasi API key diterapkan untuk memastikan keamanan komunikasi antar layanan.

Potongan kode fungsi validasinya:

```
def validate_api_key(request: Request):
    requester_domain_origin = request.headers.get("Origin")
    
    # Lookup domain key in db
    try:
        lookup_response = client.table("API_KEYS").select("*").eq("domain", requester_domain_origin).execute().data[0]["key"]
        print(request.headers.get("API-Key"))
        print(lookup_response)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Domain not found")

    return lookup_response == request.headers.get("API-Key")
```

---

## 📜 **11. Dokumentasi API**  
Endpoint didokumentasikan dengan laman web berbasis HTML, CSS, dan JS yang tersedia di [sandbox](https://taskhub-tst.vercel.app/sandbox.html), dengan dukungan mode interaktif juga!

---

## 🤝 **12. Integrasi dengan Layanan Lain**  
- **Spotify Bot:** Widget chatbot untuk mendukung kebutuhan pengguna.  

![Chatbot](https://github.com/RunningPie/Tubes-TST-2024/blob/main/docs/supporting_images/Chatbot.png)

🎉 **Terima kasih telah menggunakan TaskHub!**