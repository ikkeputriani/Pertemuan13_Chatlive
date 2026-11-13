from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT = Path(__file__).resolve().parent / "laporan-chatlive.pdf"
NAVY = colors.HexColor("#14213d")
BLUE = colors.HexColor("#3157b7")
PALE = colors.HexColor("#eef2fb")
INK = colors.HexColor("#263247")
MUTED = colors.HexColor("#63718a")

styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        "CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=30,
        leading=36,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceAfter=12,
    )
)
styles.add(
    ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=14,
        leading=21,
        textColor=MUTED,
    )
)
styles.add(
    ParagraphStyle(
        "Section",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=24,
        textColor=NAVY,
        spaceBefore=8,
        spaceAfter=11,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        "Subsection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=BLUE,
        spaceBefore=9,
        spaceAfter=5,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.4,
        leading=14,
        textColor=INK,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=MUTED,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        "TaskBullet",
        parent=styles["Body"],
        leftIndent=13,
        firstLineIndent=-8,
        bulletIndent=0,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        "TableHead",
        parent=styles["Body"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        spaceAfter=0,
    )
)
styles.add(
    ParagraphStyle(
        "TableBody",
        parent=styles["Body"],
        fontSize=7.8,
        leading=10.5,
        spaceAfter=0,
    )
)
styles.add(
    ParagraphStyle(
        "Callout",
        parent=styles["Body"],
        fontSize=9,
        leading=13,
        textColor=NAVY,
        spaceAfter=0,
    )
)
styles.add(
    ParagraphStyle(
        "CodeBlock",
        fontName="Courier",
        fontSize=7.3,
        leading=10,
        textColor=colors.HexColor("#263247"),
        backColor=PALE,
        borderColor=colors.HexColor("#dce4f2"),
        borderWidth=0.5,
        borderPadding=8,
        leftIndent=0,
        rightIndent=0,
        spaceBefore=3,
        spaceAfter=8,
    )
)


def p(text, style="Body"):
    return Paragraph(text, styles[style])


def bullet(text):
    return Paragraph(f"&bull;&nbsp; {text}", styles["TaskBullet"])


def code(text):
    return Preformatted(escape(text.strip()), styles["CodeBlock"])


def table(rows, widths, header=True):
    formatted = []
    for row_index, row in enumerate(rows):
        style = "TableHead" if header and row_index == 0 else "TableBody"
        formatted.append([p(str(cell), style) for cell in row])
    result = Table(formatted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d9e0eb")),
    ]
    if header:
        commands.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
        if len(formatted) > 1:
            commands.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]))
    else:
        commands.append(("BACKGROUND", (0, 0), (-1, -1), PALE))
    result.setStyle(TableStyle(commands))
    return result


def page_chrome(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        width, height = A4
        canvas.setStrokeColor(colors.HexColor("#dce3ee"))
        canvas.setLineWidth(0.5)
        canvas.line(22 * mm, height - 17 * mm, width - 22 * mm, height - 17 * mm)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(NAVY)
        canvas.drawString(22 * mm, height - 13 * mm, "CHATLIVE")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(width - 22 * mm, height - 13 * mm, "Laporan praktikum")
        canvas.line(22 * mm, 16 * mm, width - 22 * mm, 16 * mm)
        canvas.drawString(22 * mm, 11 * mm, "Angular 21  |  ASP.NET Core 8  |  SignalR")
        canvas.drawRightString(width - 22 * mm, 11 * mm, f"Halaman {doc.page}")
    canvas.restoreState()


story = [
    Spacer(1, 40 * mm),
    p("DOKUMENTASI TUGAS", "Small"),
    Spacer(1, 8 * mm),
    p("CHATLIVE", "CoverTitle"),
    p("Praktik komunikasi real-time menggunakan Angular 21 dan ASP.NET Core SignalR", "CoverSubtitle"),
    Spacer(1, 12 * mm),
    Table(
        [[p("KONSEP PESAN", "TableHead"), p("PRAKTIK SIGNALR", "TableHead"), p("APLIKASI", "TableHead")],
         [p("RabbitMQ dan manfaat message broker", "TableBody"),
          p("Hub, koneksi, pengiriman, dan broadcast", "TableBody"),
          p("Live chat satu ruang untuk banyak pengguna", "TableBody")]],
        colWidths=[53 * mm, 53 * mm, 53 * mm],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("BACKGROUND", (0, 1), (-1, 1), PALE),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9e0eb")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ]),
    ),
    Spacer(1, 10 * mm),
    table([
        ["Identitas Mahasiswa", "Keterangan"],
        ["Nama", "Ikke Putriani"],
        ["NIM", "2024133007"],
        ["Program Studi", "Teknik Perangkat Lunak"],
    ], [50 * mm, 112 * mm]),
    Spacer(1, 16 * mm),
    p("Dokumen ini mencakup konsep RabbitMQ, langkah praktikum SignalR, rancangan aplikasi, serta panduan menjalankan dan menguji ChatLive.", "Body"),
    Spacer(1, 5 * mm),
    p("Disusun berdasarkan instruksi tugas pada foto. Materi slide kelas tidak disertakan pada workspace; referensi teknis menggunakan dokumentasi resmi.", "Small"),
    Spacer(1, 24 * mm),
    p("NOVEMBER 2026", "Small"),
    PageBreak(),
    p("Ringkasan", "Section"),
    p("ChatLive adalah aplikasi pembelajaran yang memperlihatkan komunikasi dua arah secara real-time. Antarmuka dibuat dengan Angular 21, sedangkan ASP.NET Core 8 menyediakan endpoint SignalR. Ketika satu pengguna mengirim pesan, hub memvalidasi isi lalu menyiarkannya kepada semua client yang terhubung.", "Body"),
    p("Hasil yang dicakup", "Subsection"),
    bullet("Merangkum RabbitMQ dan kelebihan utamanya sebagai message broker."),
    bullet("Menjelaskan praktik SignalR: Hub, koneksi client, pemanggilan metode, dan broadcast."),
    bullet("Menyediakan aplikasi chat live satu ruang dengan indikator koneksi dan pengiriman pesan."),
    bullet("Menyediakan langkah instalasi, menjalankan aplikasi, dan skenario pengujian."),
    p("Teknologi", "Subsection"),
    table([
        ["Bagian", "Teknologi", "Tanggung jawab"],
        ["Antarmuka", "Angular 21 + TypeScript", "Input nama/pesan, status koneksi, dan daftar pesan."],
        ["Komunikasi", "ASP.NET Core SignalR", "Koneksi real-time dan broadcast pesan."],
        ["Transport", "WebSocket (dengan fallback SignalR)", "Mengirim event secara langsung; negosiasi dikelola SignalR."],
        ["Data demo", "Memori client", "Menampilkan pesan selama tab/aplikasi masih berjalan."],
    ], [31 * mm, 48 * mm, 83 * mm]),
    Spacer(1, 7),
    p("1. Konsep RabbitMQ", "Section"),
    p("<b>RabbitMQ</b> adalah message broker yang menerima, merutekan, dan mengantrekan pesan antara producer (pengirim) dan consumer (penerima). Producer mengirim pesan ke exchange; exchange memilih queue melalui binding dan routing key; consumer mengambil pesan dari queue lalu dapat mengirim acknowledgement setelah pemrosesan.", "Body"),
    p("Komponen utama", "Subsection"),
    table([
        ["Komponen", "Peran"],
        ["Producer", "Membuat dan mengirim pesan ke broker."],
        ["Exchange", "Menerima pesan dan menentukan queue tujuan berdasarkan jenis exchange dan binding."],
        ["Queue", "Menyimpan pesan sampai consumer mengambil dan memprosesnya."],
        ["Binding / routing key", "Aturan dan kunci untuk mengarahkan pesan dari exchange ke queue."],
        ["Consumer / acknowledgement", "Mengolah pesan; acknowledgement menandakan pesan berhasil diproses."],
    ], [44 * mm, 118 * mm]),
    p("Jenis exchange dan pola distribusi", "Subsection"),
    table([
        ["Jenis", "Cara kerja", "Contoh pemakaian"],
        ["Direct", "Routing key harus cocok tepat dengan binding.", "Mengarahkan invoice ke antrean pemrosesan tertentu."],
        ["Fanout", "Menyalin pesan ke semua queue yang terikat, tanpa memeriksa routing key.", "Menyebarkan pengumuman ke beberapa layanan."],
        ["Topic", "Routing key dicocokkan dengan pola bertitik dan wildcard.", "Mengirim event order.created ke consumer yang berlangganan order.*."],
        ["Headers", "Mencocokkan nilai header pesan, bukan routing key.", "Routing berdasarkan atribut atau kombinasi metadata."],
    ], [25 * mm, 67 * mm, 70 * mm]),
    p("Contoh alur bisnis", "Subsection"),
    p("Pada sistem pemesanan, layanan order dapat menerbitkan event OrderCreated. Exchange meneruskan event ke antrean inventori dan antrean notifikasi. Consumer inventori mengurangi stok, sedangkan consumer notifikasi mengirim email. Jika pengiriman email gagal sementara, pesan dapat tetap berada di antrean dan dicoba lagi sesuai kebijakan aplikasi. Contoh ini hanya menjelaskan pola RabbitMQ; ChatLive tidak mengirim pesan melalui RabbitMQ.", "Body"),
    p("Kelebihan RabbitMQ", "Subsection"),
    bullet("<b>Loose coupling:</b> producer dan consumer tidak harus aktif atau mengetahui detail implementasi satu sama lain pada saat yang sama."),
    bullet("<b>Asynchronous processing:</b> pekerjaan dapat masuk antrean dan diproses kemudian, sehingga request pengguna tidak perlu menunggu pekerjaan berat selesai."),
    bullet("<b>Keandalan pesan:</b> durable queue, pesan persisten, acknowledgement, dan mekanisme pemulihan membantu mengurangi risiko kehilangan pesan bila dikonfigurasi dengan benar."),
    bullet("<b>Skalabilitas:</b> beberapa consumer dapat memproses antrean yang sama untuk meningkatkan kapasitas kerja."),
    bullet("<b>Routing fleksibel:</b> exchange dan binding mendukung pola fanout, direct, topic, atau headers untuk kebutuhan distribusi yang berbeda."),
    bullet("<b>Ekosistem luas:</b> dapat menghubungkan layanan dengan bahasa pemrograman dan protokol yang beragam."),
    bullet("<b>Pengendalian aliran kerja:</b> antrean dapat membantu membatasi beban consumer dan memisahkan pekerjaan cepat dari proses latar yang lebih berat."),
    p("Kelebihan tersebut bergantung pada konfigurasi, deployment, dan pola konsumsi yang tepat. Broker menambah komponen operasional, sehingga kapasitas, antrean yang menumpuk, retry, dan dead-letter queue juga perlu dipantau.", "Body"),
    p("Catatan keandalan", "Subsection"),
    p("Durable queue menjaga definisi antrean setelah broker dimulai ulang, sedangkan persistent message meminta pesan disimpan secara persisten. Acknowledgement consumer membantu broker mengetahui pesan yang sudah selesai diproses; publisher confirm dapat membantu producer mengetahui bahwa broker menerima publikasi. Fitur-fitur tersebut perlu dipadukan dengan strategi retry dan idempotensi. Acknowledgement tidak otomatis menjamin pemrosesan tepat satu kali pada semua kondisi.", "Body"),
    PageBreak(),
    p("2. Praktik SignalR pada Angular dan ASP.NET Core", "Section"),
    p("<b>SignalR</b> adalah pustaka ASP.NET Core untuk komunikasi real-time dua arah antara server dan client. SignalR memilih transport yang tersedia (umumnya WebSocket) dan mengelola koneksi. <b>Hub</b> menyediakan metode server yang dapat dipanggil client dan event yang dapat dikirim server ke client.", "Body"),
    p("Perbedaan peran SignalR dan RabbitMQ", "Subsection"),
    table([
        ["Aspek", "SignalR", "RabbitMQ"],
        ["Tujuan umum", "Komunikasi interaktif langsung server-client.", "Distribusi pesan/pekerjaan antar layanan melalui broker."],
        ["Penerima", "Client yang sedang tersambung ke hub.", "Consumer yang mengambil pesan dari queue."],
        ["Contoh", "Chat, notifikasi langsung, dashboard live.", "Antrean email, proses latar, integrasi layanan."],
        ["Dalam demo", "Dipakai untuk mengirim dan menerima chat.", "Dijelaskan sebagai konsep, tidak dipasang pada jalur chat."],
    ], [28 * mm, 67 * mm, 67 * mm]),
    p("Alur aplikasi", "Subsection"),
    table([
        ["Langkah", "Proses"],
        ["1", "Angular membangun koneksi SignalR ke endpoint server /chat."],
        ["2", "Pengguna mengirim nama dan teks melalui metode SendMessage."],
        ["3", "ChatHub merapikan input dan memvalidasi panjang nama (maksimal 30) serta pesan (maksimal 500)."],
        ["4", "Server membuat id dan waktu UTC, lalu mengirim event ReceiveMessage ke semua client terhubung."],
        ["5", "Angular menambahkan pesan ke tampilan tanpa memuat ulang halaman."],
    ], [23 * mm, 139 * mm]),
    p("Rancangan pesan", "Subsection"),
    code("""{
  "id": "id-pesan",
  "user": "Nama pengguna",
  "content": "Isi pesan",
  "sentAt": "2026-11-13T13:00:00+00:00"
}"""),
    p("Langkah praktikum", "Subsection"),
    bullet("Buat project ASP.NET Core dan tambahkan ChatHub dengan metode SendMessage."),
    bullet("Daftarkan SignalR pada service dan petakan hub ke endpoint /chat."),
    bullet("Pada Angular, tambahkan @microsoft/signalr dan buat HubConnection melalui HubConnectionBuilder."),
    bullet("Daftarkan handler ReceiveMessage sebelum memulai koneksi agar event langsung ditangani."),
    bullet("Panggil invoke('SendMessage', nama, isi) saat form dikirim; tampilkan pesan dari event ReceiveMessage."),
    bullet("Aktifkan automatic reconnect dan indikator status untuk memberi informasi koneksi kepada pengguna."),
    p("Contoh registrasi endpoint pada server", "Subsection"),
    code("""builder.Services.AddSignalR();
app.MapHub<ChatHub>("/chat");"""),
    p("AddSignalR mendaftarkan layanan yang diperlukan oleh hub. MapHub menghubungkan URL /chat dengan ChatHub, yaitu endpoint yang akan dipakai client SignalR.", "Body"),
    p("Contoh inti pada ChatHub", "Subsection"),
    code("""public async Task SendMessage(string? user, string? content)
{
    var displayName = user?.Trim();
    var text = content?.Trim();
    if (string.IsNullOrWhiteSpace(displayName) || displayName.Length > 30)
        throw new HubException("Nama tidak valid.");
    if (string.IsNullOrWhiteSpace(text) || text.Length > 500)
        throw new HubException("Pesan tidak valid.");

    var message = new ChatMessage(
        Guid.NewGuid().ToString("N"), displayName, text, DateTimeOffset.UtcNow);
    await Clients.All.SendAsync("ReceiveMessage", message);
}"""),
    p("Metode hub memvalidasi data kembali di server; validasi form pada browser saja tidak cukup karena client dapat dimodifikasi. Clients.All menyiarkan pesan kepada semua koneksi aktif, termasuk pengirim. Untuk ruang privat, target broadcast perlu diganti menjadi grup SignalR dan server harus memeriksa hak akses ruang.", "Body"),
    p("Contoh inti pada Angular", "Subsection"),
    code("""const connection = new HubConnectionBuilder()
  .withUrl('/chat')
  .withAutomaticReconnect()
  .build();

connection.on('ReceiveMessage', (message) => addToChat(message));
await connection.start();
await connection.invoke('SendMessage', user, content);"""),
    p("withUrl menunjuk ke endpoint hub. Handler on mendaftarkan penerima event server, start memulai koneksi, dan invoke memanggil metode hub dari client. Handler sebaiknya dipasang sebelum start agar event tidak terlewat. Implementasi project juga menampilkan status koneksi dan memberi percobaan ulang manual jika koneksi awal gagal.", "Body"),
    PageBreak(),
    p("2.1 Penjelasan rinci aliran pesan", "Section"),
    table([
        ["Tahap", "Client / server", "Penjelasan"],
        ["1. Inisialisasi", "Angular", "ChatService membuat HubConnection ke /chat dan mendaftarkan handler ReceiveMessage."],
        ["2. Negosiasi", "SignalR", "Client dan server menetapkan transport yang dapat digunakan; WebSocket dipakai bila tersedia."],
        ["3. Input", "Angular", "Nama dan pesan di-trim; tombol kirim tidak aktif jika kosong atau koneksi belum aktif."],
        ["4. Pemanggilan", "Angular -> Hub", "invoke mengirim nama dan konten ke SendMessage dengan protokol SignalR."],
        ["5. Validasi", "ASP.NET Core", "Hub membatasi nama hingga 30 karakter dan isi hingga 500 karakter, serta menolak nilai kosong."],
        ["6. Distribusi", "Hub -> clients", "Server membuat id unik dan waktu UTC, kemudian mengirim ReceiveMessage ke koneksi aktif."],
        ["7. Render", "Angular", "Pesan dimasukkan ke state client dan ditampilkan sebagai teks; konten tidak dirender sebagai HTML."],
        ["8. Reconnect", "SignalR + Angular", "Jika koneksi terputus sesudah tersambung, automatic reconnect mencoba menyambungkan kembali."],
    ], [27 * mm, 34 * mm, 101 * mm]),
    p("Pengelolaan kegagalan", "Subsection"),
    bullet("Jika server tidak aktif, status antarmuka berubah menjadi tidak terhubung, dan pesan kesalahan memberi arahan untuk memeriksa server."),
    bullet("Automatic reconnect menangani putus koneksi setelah koneksi berhasil. Kegagalan koneksi pertama memerlukan percobaan ulang manual."),
    bullet("Jika pemanggilan SendMessage gagal, konten pesan tetap pada input agar pengguna dapat mencoba lagi."),
    bullet("Koneksi dan pesan ditampilkan sebagai state sementara di browser; memuat ulang halaman menghapus riwayat lokal."),
    p("Batas ukuran input dan validasi di hub mencegah data kosong atau sangat panjang diproses sebagai pesan demo. Aplikasi produksi tetap memerlukan rate limiting, autentikasi, otorisasi, logging, pemantauan, dan kebijakan penyimpanan.", "Body"),
    PageBreak(),
    p("3. Menjalankan ChatLive", "Section"),
    p("Struktur project", "Subsection"),
    code("""chat-live/
  client/       Angular 21 dan klien SignalR
  server/       ASP.NET Core 8 dan ChatHub
  docs/         PDF ini dan skrip pembuatannya
  README.md     panduan singkat project"""),
    p("Prasyarat", "Subsection"),
    bullet("Node.js 22 dan npm."),
    bullet(".NET SDK 8.0 (runtime saja tidak cukup untuk membangun atau menjalankan project)."),
    p("Jalankan server di terminal pertama dari folder chat-live:", "Body"),
    code("""dotnet run --project .\\server\\ChatLive.Server.csproj --urls http://localhost:5000"""),
    p("Endpoint pemeriksaan /health mengembalikan status ok. Jalankan client di terminal kedua:", "Body"),
    code("""Set-Location .\\client
npm install
npm start"""),
    p("Buka http://localhost:4200, masukkan nama, lalu kirim pesan. Untuk melihat broadcast, buka aplikasi pada dua tab browser. Proxy dev Angular meneruskan /chat dan /health ke http://localhost:5000.", "Body"),
    p("Fitur implementasi", "Subsection"),
    bullet("Ruang obrolan umum; setiap pesan diterima semua koneksi yang aktif."),
    bullet("Status koneksi, percobaan ulang manual, dan automatic reconnect."),
    bullet("Validasi input sisi server serta batas tampilan hingga 200 pesan per sesi browser."),
    bullet("Tata letak responsif dan label yang dapat dibaca oleh teknologi bantu."),
    p("Verifikasi", "Subsection"),
    table([
        ["Jenis", "Cara", "Hasil yang diharapkan"],
        ["Build client", "npm run build", "Bundle Angular production terbentuk."],
        ["Unit test client", "npm test -- --watch=false", "Komponen utama berhasil dirender."],
        ["Kesehatan server", "GET http://localhost:5000/health", "HTTP 200 dan status ok."],
        ["Uji dua client", "Kirim pesan dari tab pertama", "Tab kedua menerima pesan tanpa refresh."],
        ["Input tidak valid", "Kirim nama/pesan kosong atau terlalu panjang", "Server menolak input."],
        ["Putus/sambung server", "Hentikan lalu mulai ulang server", "Status koneksi berubah dan client mencoba reconnect."],
    ], [31 * mm, 55 * mm, 76 * mm]),
    Spacer(1, 5),
    p("Perintah build dan unit test merupakan validasi otomatis client. Skenario koneksi dua tab dan pemulihan koneksi adalah uji manual yang sebaiknya dilakukan saat server berjalan.", "Small"),
    p("4. Batasan, keamanan, dan kesimpulan", "Section"),
    p("Aplikasi ini adalah demonstrasi pembelajaran: chat tidak memiliki akun, room terpisah, penyimpanan riwayat, atau moderasi. Nama pengguna yang dikirim client bukan identitas terverifikasi. Karena itu, jangan mengekspos demo ini sebagai layanan publik tanpa autentikasi/otorisasi, validasi identitas, HTTPS, rate limiting, kebijakan retensi, logging, dan penyimpanan yang sesuai.", "Body"),
    p("RabbitMQ dan SignalR bukan pengganti satu sama lain. SignalR cocok untuk menyampaikan update langsung ke pengguna yang sedang online; RabbitMQ cocok untuk mengantrekan pekerjaan dan menyambungkan layanan secara asynchronous. Sistem produksi dapat memakai keduanya dengan batas peran yang jelas.", "Body"),
    p("Kesimpulan", "Subsection"),
    p("ChatLive memperagakan siklus dasar komunikasi real-time: membangun koneksi, memanggil metode hub, memvalidasi pesan, melakukan broadcast, dan memperbarui antarmuka. RabbitMQ melengkapi pemahaman arsitektur dengan pola message broker untuk pemrosesan asynchronous dan decoupled.", "Body"),
    p("Referensi", "Subsection"),
    p('1. RabbitMQ, "AMQP 0-9-1 Model Explained": <link href="https://www.rabbitmq.com/tutorials/amqp-concepts" color="#3157b7">rabbitmq.com/tutorials/amqp-concepts</link>', "Small"),
    p('2. Microsoft Learn, "ASP.NET Core SignalR": <link href="https://learn.microsoft.com/aspnet/core/signalr/introduction" color="#3157b7">learn.microsoft.com/aspnet/core/signalr/introduction</link>', "Small"),
    p('3. Microsoft Learn, "SignalR hubs": <link href="https://learn.microsoft.com/aspnet/core/signalr/hubs" color="#3157b7">learn.microsoft.com/aspnet/core/signalr/hubs</link>', "Small"),
    p('4. Angular, "Angular documentation": <link href="https://angular.dev/overview" color="#3157b7">angular.dev/overview</link>', "Small"),
    p("Dokumentasi kelas/slide tidak tersedia pada folder kerja saat penyusunan; materi tugas dirangkum dari instruksi pada foto dan sumber resmi di atas.", "Small"),
]

doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    rightMargin=24 * mm,
    leftMargin=24 * mm,
    topMargin=25 * mm,
    bottomMargin=23 * mm,
    title="ChatLive - Dokumentasi Praktikum SignalR",
    author="Ikke Putriani",
    subject="RabbitMQ, Angular 21, ASP.NET Core, dan SignalR",
)
doc.build(story, onFirstPage=page_chrome, onLaterPages=page_chrome)
print(f"PDF dibuat: {OUTPUT}")
