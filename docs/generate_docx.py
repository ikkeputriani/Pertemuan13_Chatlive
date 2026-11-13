from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUTPUT = Path(__file__).resolve().parent / "laporan-chatlive.docx"
NAVY = "14213D"
BLUE = "3157B7"
PALE = "EEF2FB"
INK = "263247"
MUTED = "63718A"
WHITE = "FFFFFF"


def shade(cell, fill):
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def set_cell_margins(cell, top=90, start=110, bottom=90, end=110):
    properties = cell._tc.get_or_add_tcPr()
    margins = properties.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        properties.append(margins)
    for edge, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = margins.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            margins.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row):
    properties = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    properties.append(repeat)


def set_cell_text(cell, text, *, header=False, font_size=8.5):
    cell.text = ""
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.line_spacing = 1.08
    run = paragraph.add_run(str(text))
    run.bold = header
    run.font.name = "Aptos"
    run.font.size = Pt(font_size)
    run.font.color.rgb = RGBColor.from_string(WHITE if header else INK)
    set_cell_margins(cell)


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    set_repeat_table_header(table.rows[0])
    for index, value in enumerate(headers):
        set_cell_text(table.rows[0].cells[index], value, header=True)
        shade(table.rows[0].cells[index], NAVY)
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        for column, value in enumerate(values):
            set_cell_text(cells[column], value)
            if row_index % 2 == 1:
                shade(cells[column], PALE)
    if widths:
        for row in table.rows:
            for index, width in enumerate(widths):
                row.cells[index].width = Inches(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_paragraph(doc, text, *, bold_prefix=None):
    paragraph = doc.add_paragraph(style="Normal")
    paragraph.paragraph_format.keep_together = True
    if bold_prefix and text.startswith(bold_prefix):
        paragraph.add_run(bold_prefix).bold = True
        paragraph.add_run(text[len(bold_prefix) :])
    else:
        paragraph.add_run(text)
    return paragraph


def add_bullet(doc, text, *, bold_prefix=None):
    paragraph = doc.add_paragraph(style="List Bullet")
    paragraph.paragraph_format.keep_together = True
    paragraph.paragraph_format.space_after = Pt(3)
    if bold_prefix and text.startswith(bold_prefix):
        paragraph.add_run(bold_prefix).bold = True
        paragraph.add_run(text[len(bold_prefix) :])
    else:
        paragraph.add_run(text)
    return paragraph


def add_code(doc, text):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.left_indent = Inches(0.18)
    paragraph.paragraph_format.right_indent = Inches(0.12)
    paragraph.paragraph_format.space_before = Pt(2)
    paragraph.paragraph_format.space_after = Pt(8)
    paragraph.paragraph_format.keep_together = True
    properties = paragraph._p.get_or_add_pPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), PALE)
    properties.append(shading)
    for index, line in enumerate(text.strip("\n").splitlines()):
        if index:
            paragraph.add_run().add_break()
        run = paragraph.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor.from_string(INK)
    return paragraph


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("Halaman ")
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor.from_string(MUTED)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    paragraph._p.append(field)


doc = Document()
section = doc.sections[0]
section.top_margin = Inches(0.78)
section.bottom_margin = Inches(0.72)
section.left_margin = Inches(0.88)
section.right_margin = Inches(0.88)

normal = doc.styles["Normal"]
normal.font.name = "Aptos"
normal.font.size = Pt(10)
normal.font.color.rgb = RGBColor.from_string(INK)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15

for style_name, size, color in (
    ("Title", 30, NAVY),
    ("Heading 1", 19, NAVY),
    ("Heading 2", 12, BLUE),
    ("Heading 3", 10.5, BLUE),
):
    style = doc.styles[style_name]
    style.font.name = "Aptos Display" if style_name != "Heading 3" else "Aptos"
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = RGBColor.from_string(color)
    style.paragraph_format.keep_with_next = True
    style.paragraph_format.space_before = Pt(10 if style_name != "Title" else 0)
    style.paragraph_format.space_after = Pt(5)

header = section.header.paragraphs[0]
header.text = "CHATLIVE  |  LAPORAN PRAKTIKUM SIGNALR"
header.style = doc.styles["Caption"]
header.runs[0].font.color.rgb = RGBColor.from_string(MUTED)
header.runs[0].font.size = Pt(8)

footer = section.footer.paragraphs[0]
footer.add_run("Angular 21  |  ASP.NET Core 8  |  SignalR").font.size = Pt(8)
footer.runs[0].font.color.rgb = RGBColor.from_string(MUTED)
add_page_number(section.footer.add_paragraph())

doc.core_properties.title = "ChatLive - Laporan Praktikum SignalR"
doc.core_properties.subject = "RabbitMQ, Angular 21, ASP.NET Core, dan SignalR"
doc.core_properties.author = "Ikke Putriani"
doc.core_properties.keywords = "RabbitMQ, SignalR, Angular, ASP.NET Core, ChatLive"

# Sampul
for _ in range(3):
    doc.add_paragraph()
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(10)
r = p.add_run("DOKUMENTASI TUGAS")
r.bold = True
r.font.size = Pt(10)
r.font.color.rgb = RGBColor.from_string(BLUE)

p = doc.add_paragraph(style="Title")
p.add_run("CHATLIVE")
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(20)
r = p.add_run(
    "Praktik komunikasi real-time menggunakan Angular 21 "
    "dan ASP.NET Core SignalR"
)
r.font.size = Pt(15)
r.font.color.rgb = RGBColor.from_string(MUTED)

add_table(
    doc,
    ["KONSEP PESAN", "PRAKTIK SIGNALR", "APLIKASI"],
    [[
        "RabbitMQ dan manfaat message broker",
        "Hub, koneksi, pengiriman, dan broadcast",
        "Live chat satu ruang untuk banyak pengguna",
    ]],
    [2.05, 2.05, 2.05],
)
add_table(
    doc,
    ["Identitas Mahasiswa", "Keterangan"],
    [
        ["Nama", "Ikke Putriani"],
        ["NIM", "2024133007"],
        ["Program Studi", "Teknik Perangkat Lunak"],
    ],
    [1.8, 4.2],
)
add_paragraph(
    doc,
    "Dokumen ini mencakup konsep RabbitMQ, langkah praktikum SignalR, "
    "rancangan aplikasi, serta panduan menjalankan dan menguji ChatLive.",
)
add_paragraph(
    doc,
    "Disusun berdasarkan instruksi tugas pada foto. Materi slide kelas tidak "
    "disertakan pada workspace; referensi teknis menggunakan dokumentasi resmi.",
)
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(25)
r = p.add_run("NOVEMBER 2026")
r.bold = True
r.font.size = Pt(9)
r.font.color.rgb = RGBColor.from_string(MUTED)

doc.add_page_break()

# Ringkasan
doc.add_heading("Ringkasan", level=1)
add_paragraph(
    doc,
    "ChatLive adalah aplikasi pembelajaran yang memperlihatkan komunikasi dua "
    "arah secara real-time. Antarmuka dibuat dengan Angular 21, sedangkan "
    "ASP.NET Core 8 menyediakan endpoint SignalR. Ketika satu pengguna "
    "mengirim pesan, hub memvalidasi isi lalu menyiarkannya kepada semua client "
    "yang terhubung.",
)
doc.add_heading("Hasil yang dicakup", level=2)
for item in [
    "Merangkum RabbitMQ dan kelebihan utamanya sebagai message broker.",
    "Menjelaskan praktik SignalR: Hub, koneksi client, pemanggilan metode, dan broadcast.",
    "Menyediakan aplikasi chat live satu ruang dengan indikator koneksi dan pengiriman pesan.",
    "Menyediakan langkah instalasi, menjalankan aplikasi, dan skenario pengujian.",
]:
    add_bullet(doc, item)
doc.add_heading("Teknologi", level=2)
add_table(
    doc,
    ["Bagian", "Teknologi", "Tanggung jawab"],
    [
        ["Antarmuka", "Angular 21 + TypeScript", "Input nama/pesan, status koneksi, dan daftar pesan."],
        ["Komunikasi", "ASP.NET Core SignalR", "Koneksi real-time dan broadcast pesan."],
        ["Transport", "WebSocket (dengan fallback SignalR)", "Mengirim event secara langsung; negosiasi dikelola SignalR."],
        ["Data demo", "Memori client", "Menampilkan pesan selama tab/aplikasi masih berjalan."],
    ],
    [1.05, 1.7, 3.5],
)

# 1. RabbitMQ
doc.add_heading("1. Konsep RabbitMQ", level=1)
add_paragraph(
    doc,
    "RabbitMQ adalah message broker yang menerima, merutekan, dan "
    "mengantrekan pesan antara producer (pengirim) dan consumer (penerima). "
    "Producer mengirim pesan ke exchange; exchange memilih queue melalui "
    "binding dan routing key; consumer mengambil pesan dari queue lalu dapat "
    "mengirim acknowledgement setelah pemrosesan.",
)
doc.add_heading("Komponen utama", level=2)
add_table(
    doc,
    ["Komponen", "Peran"],
    [
        ["Producer", "Membuat dan mengirim pesan ke broker."],
        ["Exchange", "Menerima pesan dan menentukan queue tujuan berdasarkan jenis exchange dan binding."],
        ["Queue", "Menyimpan pesan sampai consumer mengambil dan memprosesnya."],
        ["Binding / routing key", "Aturan dan kunci untuk mengarahkan pesan dari exchange ke queue."],
        ["Consumer / acknowledgement", "Mengolah pesan; acknowledgement menandakan pesan berhasil diproses."],
    ],
    [1.8, 4.3],
)
doc.add_heading("Jenis exchange dan pola distribusi", level=2)
add_table(
    doc,
    ["Jenis", "Cara kerja", "Contoh pemakaian"],
    [
        ["Direct", "Routing key harus cocok tepat dengan binding.", "Mengarahkan invoice ke antrean pemrosesan tertentu."],
        ["Fanout", "Menyalin pesan ke semua queue yang terikat, tanpa memeriksa routing key.", "Menyebarkan pengumuman ke beberapa layanan."],
        ["Topic", "Routing key dicocokkan dengan pola bertitik dan wildcard.", "Mengirim event order.created ke consumer yang berlangganan order.*."],
        ["Headers", "Mencocokkan nilai header pesan, bukan routing key.", "Routing berdasarkan atribut atau kombinasi metadata."],
    ],
    [0.85, 2.65, 2.6],
)
doc.add_heading("Contoh alur bisnis", level=2)
add_paragraph(
    doc,
    "Pada sistem pemesanan, layanan order dapat menerbitkan event OrderCreated. "
    "Exchange meneruskan event ke antrean inventori dan antrean notifikasi. "
    "Consumer inventori mengurangi stok, sedangkan consumer notifikasi "
    "mengirim email. Jika pengiriman email gagal sementara, pesan dapat tetap "
    "berada di antrean dan dicoba lagi sesuai kebijakan aplikasi. Contoh ini "
    "hanya menjelaskan pola RabbitMQ; ChatLive tidak mengirim pesan melalui RabbitMQ.",
)
doc.add_heading("Kelebihan RabbitMQ", level=2)
for label, text in [
    ("Loose coupling:", " producer dan consumer tidak harus aktif atau mengetahui detail implementasi satu sama lain pada saat yang sama."),
    ("Asynchronous processing:", " pekerjaan dapat masuk antrean dan diproses kemudian, sehingga request pengguna tidak perlu menunggu pekerjaan berat selesai."),
    ("Keandalan pesan:", " durable queue, pesan persisten, acknowledgement, dan mekanisme pemulihan membantu mengurangi risiko kehilangan pesan bila dikonfigurasi dengan benar."),
    ("Skalabilitas:", " beberapa consumer dapat memproses antrean yang sama untuk meningkatkan kapasitas kerja."),
    ("Routing fleksibel:", " exchange dan binding mendukung pola fanout, direct, topic, atau headers untuk kebutuhan distribusi yang berbeda."),
    ("Ekosistem luas:", " dapat menghubungkan layanan dengan bahasa pemrograman dan protokol yang beragam."),
    ("Pengendalian aliran kerja:", " antrean dapat membantu membatasi beban consumer dan memisahkan pekerjaan cepat dari proses latar yang lebih berat."),
]:
    add_bullet(doc, label + text, bold_prefix=label)
add_paragraph(
    doc,
    "Kelebihan tersebut bergantung pada konfigurasi, deployment, dan pola "
    "konsumsi yang tepat. Broker menambah komponen operasional, sehingga "
    "kapasitas, antrean yang menumpuk, retry, dan dead-letter queue juga perlu dipantau.",
)
doc.add_heading("Catatan keandalan", level=2)
add_paragraph(
    doc,
    "Durable queue menjaga definisi antrean setelah broker dimulai ulang, "
    "sedangkan persistent message meminta pesan disimpan secara persisten. "
    "Acknowledgement consumer membantu broker mengetahui pesan yang sudah "
    "selesai diproses; publisher confirm dapat membantu producer mengetahui "
    "bahwa broker menerima publikasi. Fitur-fitur tersebut perlu dipadukan "
    "dengan strategi retry dan idempotensi. Acknowledgement tidak otomatis "
    "menjamin pemrosesan tepat satu kali pada semua kondisi.",
)

# 2. Praktik SignalR
doc.add_page_break()
doc.add_heading("2. Praktik SignalR pada Angular dan ASP.NET Core", level=1)
add_paragraph(
    doc,
    "SignalR adalah pustaka ASP.NET Core untuk komunikasi real-time dua arah "
    "antara server dan client. SignalR memilih transport yang tersedia "
    "(umumnya WebSocket) dan mengelola koneksi. Hub menyediakan metode server "
    "yang dapat dipanggil client dan event yang dapat dikirim server ke client.",
)
doc.add_heading("Perbedaan peran SignalR dan RabbitMQ", level=2)
add_table(
    doc,
    ["Aspek", "SignalR", "RabbitMQ"],
    [
        ["Tujuan umum", "Komunikasi interaktif langsung server-client.", "Distribusi pesan/pekerjaan antar layanan melalui broker."],
        ["Penerima", "Client yang sedang tersambung ke hub.", "Consumer yang mengambil pesan dari queue."],
        ["Contoh", "Chat, notifikasi langsung, dashboard live.", "Antrean email, proses latar, integrasi layanan."],
        ["Dalam demo", "Dipakai untuk mengirim dan menerima chat.", "Dijelaskan sebagai konsep, tidak dipasang pada jalur chat."],
    ],
    [1.0, 2.55, 2.55],
)
doc.add_heading("Alur aplikasi", level=2)
add_table(
    doc,
    ["Langkah", "Proses"],
    [
        ["1", "Angular membangun koneksi SignalR ke endpoint server /chat."],
        ["2", "Pengguna mengirim nama dan teks melalui metode SendMessage."],
        ["3", "ChatHub merapikan input dan memvalidasi panjang nama (maksimal 30) serta pesan (maksimal 500)."],
        ["4", "Server membuat id dan waktu UTC, lalu mengirim event ReceiveMessage ke semua client terhubung."],
        ["5", "Angular menambahkan pesan ke tampilan tanpa memuat ulang halaman."],
    ],
    [0.6, 5.5],
)
doc.add_heading("Rancangan pesan", level=2)
add_code(
    doc,
    """{
  "id": "id-pesan",
  "user": "Nama pengguna",
  "content": "Isi pesan",
  "sentAt": "2026-11-13T13:00:00+00:00"
}""",
)
doc.add_heading("Langkah praktikum", level=2)
for item in [
    "Buat project ASP.NET Core dan tambahkan ChatHub dengan metode SendMessage.",
    "Daftarkan SignalR pada service dan petakan hub ke endpoint /chat.",
    "Pada Angular, tambahkan @microsoft/signalr dan buat HubConnection melalui HubConnectionBuilder.",
    "Daftarkan handler ReceiveMessage sebelum memulai koneksi agar event langsung ditangani.",
    "Panggil invoke('SendMessage', nama, isi) saat form dikirim; tampilkan pesan dari event ReceiveMessage.",
    "Aktifkan automatic reconnect dan indikator status untuk memberi informasi koneksi kepada pengguna.",
]:
    add_bullet(doc, item)
doc.add_heading("Contoh registrasi endpoint pada server", level=2)
add_code(
    doc,
    """builder.Services.AddSignalR();
app.MapHub<ChatHub>("/chat");""",
)
add_paragraph(
    doc,
    "AddSignalR mendaftarkan layanan yang diperlukan oleh hub. MapHub "
    "menghubungkan URL /chat dengan ChatHub, yaitu endpoint yang akan dipakai client SignalR.",
)
doc.add_heading("Contoh inti pada ChatHub", level=2)
add_code(
    doc,
    """public async Task SendMessage(string? user, string? content)
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
}""",
)
add_paragraph(
    doc,
    "Metode hub memvalidasi data kembali di server; validasi form pada browser "
    "saja tidak cukup karena client dapat dimodifikasi. Clients.All menyiarkan "
    "pesan kepada semua koneksi aktif, termasuk pengirim. Untuk ruang privat, "
    "target broadcast perlu diganti menjadi grup SignalR dan server harus "
    "memeriksa hak akses ruang.",
)
doc.add_heading("Contoh inti pada Angular", level=2)
add_code(
    doc,
    """const connection = new HubConnectionBuilder()
  .withUrl('/chat')
  .withAutomaticReconnect()
  .build();

connection.on('ReceiveMessage', (message) => addToChat(message));
await connection.start();
await connection.invoke('SendMessage', user, content);""",
)
add_paragraph(
    doc,
    "withUrl menunjuk ke endpoint hub. Handler on mendaftarkan penerima event "
    "server, start memulai koneksi, dan invoke memanggil metode hub dari client. "
    "Handler sebaiknya dipasang sebelum start agar event tidak terlewat. "
    "Implementasi project juga menampilkan status koneksi dan memberi "
    "percobaan ulang manual jika koneksi awal gagal.",
)

# 2.1 Aliran pesan
doc.add_page_break()
doc.add_heading("2.1 Penjelasan rinci aliran pesan", level=1)
add_table(
    doc,
    ["Tahap", "Client / server", "Penjelasan"],
    [
        ["1. Inisialisasi", "Angular", "ChatService membuat HubConnection ke /chat dan mendaftarkan handler ReceiveMessage."],
        ["2. Negosiasi", "SignalR", "Client dan server menetapkan transport yang dapat digunakan; WebSocket dipakai bila tersedia."],
        ["3. Input", "Angular", "Nama dan pesan di-trim; tombol kirim tidak aktif jika kosong atau koneksi belum aktif."],
        ["4. Pemanggilan", "Angular -> Hub", "invoke mengirim nama dan konten ke SendMessage dengan protokol SignalR."],
        ["5. Validasi", "ASP.NET Core", "Hub membatasi nama hingga 30 karakter dan isi hingga 500 karakter, serta menolak nilai kosong."],
        ["6. Distribusi", "Hub -> clients", "Server membuat id unik dan waktu UTC, kemudian mengirim ReceiveMessage ke koneksi aktif."],
        ["7. Render", "Angular", "Pesan dimasukkan ke state client dan ditampilkan sebagai teks; konten tidak dirender sebagai HTML."],
        ["8. Reconnect", "SignalR + Angular", "Jika koneksi terputus sesudah koneksi berhasil, automatic reconnect mencoba menyambungkan kembali."],
    ],
    [1.15, 1.15, 3.8],
)
doc.add_heading("Pengelolaan kegagalan", level=2)
for item in [
    "Jika server tidak aktif, status antarmuka berubah menjadi tidak terhubung dan pesan kesalahan memberi arahan untuk memeriksa server.",
    "Automatic reconnect menangani putus koneksi setelah koneksi berhasil. Kegagalan koneksi pertama memerlukan percobaan ulang manual.",
    "Jika pemanggilan SendMessage gagal, konten pesan tetap pada input agar pengguna dapat mencoba lagi.",
    "Koneksi dan pesan ditampilkan sebagai state sementara di browser; memuat ulang halaman menghapus riwayat lokal.",
]:
    add_bullet(doc, item)
add_paragraph(
    doc,
    "Batas ukuran input dan validasi di hub mencegah data kosong atau sangat "
    "panjang diproses sebagai pesan demo. Aplikasi produksi tetap memerlukan "
    "rate limiting, autentikasi, otorisasi, logging, pemantauan, dan kebijakan penyimpanan.",
)

# 3. Menjalankan aplikasi
doc.add_page_break()
doc.add_heading("3. Menjalankan ChatLive", level=1)
doc.add_heading("Struktur project", level=2)
add_code(
    doc,
    """chat-live/
  client/       Angular 21 dan klien SignalR
  server/       ASP.NET Core 8 dan ChatHub
  docs/         PDF dan dokumen Word
  README.md     panduan singkat project""",
)
doc.add_heading("Prasyarat", level=2)
add_bullet(doc, "Node.js 22 dan npm.")
add_bullet(doc, ".NET SDK 8.0 (runtime saja tidak cukup untuk membangun atau menjalankan project).")
doc.add_heading("Menjalankan server", level=2)
add_paragraph(doc, "Jalankan server di terminal pertama dari folder chat-live:")
add_code(
    doc,
    """dotnet run --project .\\server\\ChatLive.Server.csproj --urls http://localhost:5000""",
)
add_paragraph(
    doc,
    "Endpoint pemeriksaan /health mengembalikan status ok. Jalankan client di terminal kedua:",
)
add_code(
    doc,
    """Set-Location .\\client
npm install
npm start""",
)
add_paragraph(
    doc,
    "Buka http://localhost:4200, masukkan nama, lalu kirim pesan. Untuk melihat "
    "broadcast, buka aplikasi pada dua tab browser. Proxy dev Angular "
    "meneruskan /chat dan /health ke http://localhost:5000.",
)
doc.add_heading("Fitur implementasi", level=2)
for item in [
    "Ruang obrolan umum; setiap pesan diterima semua koneksi yang aktif.",
    "Status koneksi, percobaan ulang manual, dan automatic reconnect.",
    "Validasi input sisi server serta batas tampilan hingga 200 pesan per sesi browser.",
    "Tata letak responsif dan label yang dapat dibaca oleh teknologi bantu.",
]:
    add_bullet(doc, item)
doc.add_heading("Verifikasi", level=2)
add_table(
    doc,
    ["Jenis", "Cara", "Hasil yang diharapkan"],
    [
        ["Build client", "npm run build", "Bundle Angular production terbentuk."],
        ["Unit test client", "npm test -- --watch=false", "Komponen utama berhasil dirender."],
        ["Kesehatan server", "GET http://localhost:5000/health", "HTTP 200 dan status ok."],
        ["Uji dua client", "Kirim pesan dari tab pertama", "Tab kedua menerima pesan tanpa refresh."],
        ["Input tidak valid", "Kirim nama/pesan kosong atau terlalu panjang", "Server menolak input."],
        ["Putus/sambung server", "Hentikan lalu mulai ulang server", "Status koneksi berubah dan client mencoba reconnect."],
    ],
    [1.15, 2.1, 2.85],
)
add_paragraph(
    doc,
    "Perintah build dan unit test merupakan validasi otomatis client. Skenario "
    "koneksi dua tab dan pemulihan koneksi adalah uji manual yang sebaiknya dilakukan saat server berjalan.",
)

# 4. Batasan dan kesimpulan
doc.add_heading("4. Batasan, keamanan, dan kesimpulan", level=1)
add_paragraph(
    doc,
    "Aplikasi ini adalah demonstrasi pembelajaran: chat tidak memiliki akun, "
    "room terpisah, penyimpanan riwayat, atau moderasi. Nama pengguna yang "
    "dikirim client bukan identitas terverifikasi. Karena itu, jangan "
    "mengekspos demo ini sebagai layanan publik tanpa autentikasi/otorisasi, "
    "validasi identitas, HTTPS, rate limiting, kebijakan retensi, logging, dan "
    "penyimpanan yang sesuai.",
)
add_paragraph(
    doc,
    "RabbitMQ dan SignalR bukan pengganti satu sama lain. SignalR cocok untuk "
    "menyampaikan update langsung ke pengguna yang sedang online; RabbitMQ "
    "cocok untuk mengantrekan pekerjaan dan menyambungkan layanan secara "
    "asynchronous. Sistem produksi dapat memakai keduanya dengan batas peran yang jelas.",
)
doc.add_heading("Kesimpulan", level=2)
add_paragraph(
    doc,
    "ChatLive memperagakan siklus dasar komunikasi real-time: membangun "
    "koneksi, memanggil metode hub, memvalidasi pesan, melakukan broadcast, "
    "dan memperbarui antarmuka. RabbitMQ melengkapi pemahaman arsitektur "
    "dengan pola message broker untuk pemrosesan asynchronous dan decoupled.",
)
doc.add_heading("Referensi", level=2)
references = [
    'RabbitMQ, "AMQP 0-9-1 Model Explained": https://www.rabbitmq.com/tutorials/amqp-concepts',
    'Microsoft Learn, "ASP.NET Core SignalR": https://learn.microsoft.com/aspnet/core/signalr/introduction',
    'Microsoft Learn, "SignalR hubs": https://learn.microsoft.com/aspnet/core/signalr/hubs',
    'Angular, "Angular documentation": https://angular.dev/overview',
]
for reference in references:
    add_bullet(doc, reference)
add_paragraph(
    doc,
    "Dokumentasi kelas/slide tidak tersedia pada folder kerja saat penyusunan; "
    "materi tugas dirangkum dari instruksi pada foto dan sumber resmi di atas.",
)

doc.save(OUTPUT)
print(f"Dokumen Word dibuat: {OUTPUT}")
