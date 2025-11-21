# POS Employee Access Control Module - Odoo 18

Module ini memberikan kontrol akses yang detail untuk employee di Point of Sale (POS).

## Fitur

Module ini mengontrol akses employee untuk operasi berikut:

1. **POS Closing** - Menutup sesi POS
2. **Order Deletion/Cancellation** - Menghapus atau membatalkan order
3. **Order Line Deletion** - Menghapus baris order
4. **Order Payment** - Memproses pembayaran
5. **Discount Application** - Menerapkan diskon
6. **Price Change** - Mengubah harga produk
7. **Decreasing Quantity** - Mengurangi kuantitas produk
8. **Cash In/Out** - Operasi kas masuk/keluar
9. **Create Product** - Membuat produk baru dari POS
10. **Fiscal Position/Tax** - Mengubah posisi fiskal atau pajak
11. **Pricelist** - Mengubah pricelist
12. **Refund** - Memproses pengembalian

## Perbaikan yang Dilakukan

### Versi 1.0.1 (Latest)
- ✅ Memperbaiki import module yang salah untuk Odoo 18
- ✅ Menggunakan `PosOrder` dan `PosOrderline` yang benar
- ✅ Memperbaiki method yang tidak ada di model standar
- ✅ Menambahkan `AlertDialog` import yang hilang
- ✅ Memisahkan logika ke file-file terpisah untuk maintainability
- ✅ Memperbaiki loading employee access saat startup
- ✅ Menambahkan error handling untuk API calls
- ✅ Memperbaiki XML template yang conflict
- ✅ Menambahkan file manifest yang lengkap

## Instalasi

1. Copy folder `pos_employee_access` ke direktori addons Odoo Anda
2. Restart Odoo server
3. Update Apps List
4. Cari module "POS Employee Access Control"
5. Klik Install

## Konfigurasi

1. Buka menu **Employees** (HR > Employees)
2. Pilih employee yang ingin dikonfigurasi
3. Buka tab **POS Access Control**
4. Centang atau hapus centang permission sesuai kebutuhan:
   - **Default**: Semua permission dicentang (employee bisa melakukan semua operasi)
   - **Restricted**: Hapus centang untuk melarang operasi tertentu

## Cara Kerja

### Contoh: Membatasi Akses Refund

1. Buka employee profile (misal: Employee "John Doe")
2. Masuk ke tab "POS Access Control"
3. **Hilangkan centang** pada "Allow Refund"
4. Save

Ketika John Doe login ke POS dan mencoba melakukan refund:
- Tombol refund akan terblokir
- Alert muncul: "You don't have permission to perform this operation: Refund"
- Operasi refund tidak akan dijalankan

### Blocking Mechanism

Module ini memblokir aksi menggunakan tiga cara:
1. **Mouse Input** - Click event terblokir
2. **Keyboard Input** - Keyboard shortcut terblokir
3. **Touch Input** - Touch event terblokir (untuk layar sentuh)


## Teknis

### Backend (Python)

- **Model**: `hr.employee` (inherit)
- **Fields**: 12 boolean fields untuk setiap permission
- **Method**: `get_pos_employee_access()` untuk load permission ke frontend

### Frontend (JavaScript)

File-file JavaScript yang digunakan:

1. **pos_employee_access.js** - Core functionality
   - Load employee access permissions
   - Check access method
   - Alert dialog untuk access denied
   - Patch `PosStore`, `PosOrder`, `PosOrderline`

2. **payment_override.js** - Payment control
   - Patch `PaymentScreen` untuk validasi payment
   - Patch `ActionpadWidget` untuk submit order button

3. **refund_override.js** - Refund control
   - Patch `TicketScreen` untuk refund operations

4. **order_operations.js** - Order & Line deletion control
   - Patch `ProductScreen` untuk delete order
   - Patch `Orderline` component untuk delete line

5. **session_operations.js** - Session control
   - Patch `CashOpeningPopup` untuk cash in/out

6. **discount_operations.js** - Discount control
   - Patch `NumberPopup` untuk discount validation

7. **product_operations.js** - Product creation control
   - Patch `ProductScreen` untuk create product

8. **fiscal_pricelist_operations.js** - Fiscal & Pricelist control
   - Patch `PartnerListScreen` untuk pricelist dan fiscal position changes

### Views (XML)

- Form view inheritance untuk Employee dengan tab "POS Access Control"
- Minimal XML templates (kontrol utama di JavaScript)

## Keamanan

Permission divalidasi di:
1. **Backend**: Method calls di Python
2. **Frontend**: JavaScript patches dan event listeners
3. **UI Level**: Data attributes pada buttons

## Testing

### Cara Test Module

1. **Install Module**
   ```bash
   # Restart Odoo
   # Update module list
   # Install pos_employee_access
   ```

2. **Setup Test Employee**
   - Buka HR > Employees
   - Pilih atau buat employee baru
   - Buka tab "POS Access Control"
   - Hilangkan centang pada beberapa permission (misal: "Allow Refund")
   - Save

3. **Test di POS**
   - Login ke POS dengan employee yang sudah dikonfigurasi
   - Coba lakukan operasi yang dilarang (misal: Refund)
   - Seharusnya muncul alert "Access Denied"
   - Operasi tidak akan dijalankan

4. **Test Scenarios**
   - ❌ **Refund**: Hilangkan "Allow Refund" → Coba refund order
   - ❌ **Payment**: Hilangkan "Allow Payment" → Coba bayar order
   - ❌ **Discount**: Hilangkan "Allow Discount" → Coba beri diskon
   - ❌ **Price Change**: Hilangkan "Allow Price Change" → Coba ubah harga
   - ❌ **Qty Decrease**: Hilangkan "Allow Qty Decrease" → Coba kurangi qty
   - ❌ **Delete Line**: Hilangkan "Allow Order Line Deletion" → Coba hapus line
   - ❌ **Delete Order**: Hilangkan "Allow Order Deletion" → Coba hapus order
   - ❌ **Cash In/Out**: Hilangkan "Allow Cash In/Out" → Coba cash in/out
   - ❌ **Close Session**: Hilangkan "Allow POS Closing" → Coba close session

## Troubleshooting

### Permission tidak bekerja
- Pastikan employee sudah di-set di POS session
- Refresh browser (Ctrl+F5)
- Check console browser untuk error
- Pastikan module sudah di-upgrade setelah update

### Error saat load
- Check log Odoo untuk error Python
- Pastikan dependency (`point_of_sale`, `hr`) sudah terinstall
- Clear browser cache

## Compatibility

- **Odoo Version**: 18.0
- **Dependencies**: `point_of_sale`, `hr`

## Support

Untuk bantuan atau pertanyaan, hubungi administrator sistem Anda.


