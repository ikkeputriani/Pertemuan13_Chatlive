# ChatLive

Aplikasi chat real-time untuk praktik SignalR menggunakan Angular 21 dan ASP.NET Core 8. Laporan tugas Word yang dapat diedit tersedia pada [`docs/laporan-chatlive.docx`](./docs/laporan-chatlive.docx). PDF versi sebelumnya juga tersedia pada [`docs/laporan-chatlive.pdf`](./docs/laporan-chatlive.pdf).

## Persyaratan

- Node.js 22 LTS atau kompatibel dengan Angular 21
- .NET SDK 8.0
- npm

## Menjalankan aplikasi

1. Jalankan server pada terminal pertama:

   ```powershell
   dotnet run --project .\server\ChatLive.Server.csproj --urls http://localhost:5000
   ```

2. Pastikan server aktif dengan membuka `http://localhost:5000/health`. Respons yang diharapkan: `{"status":"ok"}`.

3. Pada terminal kedua, pasang dependency dan jalankan aplikasi web:

   ```powershell
   Set-Location .\client
   npm install
   npm start
   ```

4. Buka `http://localhost:4200`, isi nama, lalu kirim pesan. Buka halaman pada tab atau perangkat lain di jaringan yang sama untuk menguji pesan real-time.

Frontend meneruskan koneksi `/chat` ke server melalui konfigurasi proxy Angular. Untuk akses dari perangkat lain, ubah alamat server/proxy dan konfigurasi CORS sesuai alamat asal frontend.

## Alur komunikasi

1. Angular membuat koneksi SignalR ke endpoint `/chat`.
2. Client memanggil metode hub `SendMessage` dengan nama dan isi pesan.
3. `ChatHub` memvalidasi panjang dan nilai masukan.
4. Server mengirim event `ReceiveMessage` kepada semua client yang sedang terhubung.
5. Angular memperbarui tampilan tanpa memuat ulang halaman.

## Batasan dan keamanan

- Pesan disimpan sementara di memori browser; server tidak menyimpan riwayat.
- Nama pengguna tidak diautentikasi dan dapat dipalsukan. Aplikasi ini untuk pembelajaran, bukan penggunaan produksi.
- Penggunaan nyata memerlukan autentikasi/otorisasi, penyimpanan pesan, pembatasan laju, pengelolaan room, logging, dan konfigurasi HTTPS.
- RabbitMQ adalah broker pesan untuk komunikasi asynchronous antar layanan. RabbitMQ tidak dipakai pada aplikasi demo ini: SignalR menangani komunikasi langsung antara server dan client chat, sedangkan RabbitMQ cocok untuk antrean kerja dan integrasi layanan.

## Verifikasi

```powershell
Set-Location .\client
npm run build
npm test -- --watch=false
```
