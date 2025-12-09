from odoo import models, _
from collections import defaultdict

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _add_mls_related_to_order(self, related_order_lines, are_qties_done=True):
        """
        Override to handle multi-UoM conversion between POS order lines and stock moves
        with support for multiple UoMs and lots in single transaction.
        """
        # --- Jalankan logic bawaan dulu ---
        res = super()._add_mls_related_to_order(related_order_lines, are_qties_done)
        
        # --- Patch konversi qty dari POS UoM ke stock UoM per line ---
        for move in self:
            product = move.product_id
            product_uom = product.uom_id
            
            # Filter order line yang terkait produk ini
            pos_lines = related_order_lines.filtered(lambda l: l.product_id == product)
            if not pos_lines:
                continue
            
            # Jika produk tidak pakai tracking atau tidak pakai lots, handle langsung
            if product.tracking == 'none' or (not move.picking_type_id.use_existing_lots and not move.picking_type_id.use_create_lots):
                # Hitung total qty terkonversi
                total_qty = 0.0
                for line in pos_lines:
                    line_uom = getattr(line, 'product_uom', False) or getattr(line, 'product_uom_id', False) or product_uom
                    qty_converted = line_uom._compute_quantity(abs(line.qty), product_uom, rounding_method='HALF-UP')
                    total_qty += qty_converted
                
                # Update quantity done
                if are_qties_done:
                    move.quantity = total_qty
                
                # Update product_uom_qty (planned qty)
                if total_qty and abs(move.product_uom_qty - total_qty) > 1e-6:
                    move.product_uom_qty = total_qty
                
                continue
            
            # --- Handle produk dengan tracking (serial/lot) ---
            if not move.move_line_ids:
                continue
            
            # Build mapping: lot_name -> (pos_line, pack_lot)
            lot_to_pos_line = {}
            for pos_line in pos_lines:
                for pack_lot in pos_line.pack_lot_ids.filtered(lambda l: l.lot_name):
                    lot_to_pos_line[pack_lot.lot_name] = (pos_line, pack_lot)
            
            # Update setiap move line dengan qty yang benar
            total_qty = 0.0
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info(f"=== Processing move {move.id} for product {product.name} ===")
            _logger.info(f"Move lines count: {len(move.move_line_ids)}")
            _logger.info(f"Lot mapping: {lot_to_pos_line.keys()}")
            
            for ml in move.move_line_ids:
                # Cari lot name dari move line
                lot_name = ml.lot_name or (ml.lot_id.name if ml.lot_id else False)
                
                if not lot_name or lot_name not in lot_to_pos_line:
                    continue
                
                pos_line, pack_lot = lot_to_pos_line[lot_name]
                
                # Ambil UoM dari POS line
                line_uom = getattr(pos_line, 'product_uom', False) or getattr(pos_line, 'product_uom_id', False) or product_uom
                
                # Hitung qty untuk lot ini
                if product.tracking == 'serial':
                    qty_for_lot = 1.0
                else:
                    # Konversi qty dari UoM POS ke UoM produk
                    qty_for_lot = line_uom._compute_quantity(
                        abs(pos_line.qty),
                        product_uom,
                        rounding_method='HALF-UP'
                    )
                
                # Update qty_done di move line
                if are_qties_done:
                    ml.qty_done = qty_for_lot
                    ml.quantity_product_uom = qty_for_lot
                
                _logger.info(f"ML {ml.id} - Lot: {lot_name}, UoM: {line_uom.name}, Qty: {qty_for_lot}")
                
                total_qty += qty_for_lot
            
            # Update product_uom_qty di move (total planned)
            if total_qty and abs(move.product_uom_qty - total_qty) > 1e-6:
                move.product_uom_qty = total_qty
        
        return res

# from odoo import models, _
# from odoo.tools import float_round
# from collections import defaultdict
# import math

# class StockMove(models.Model):
#     _inherit = 'stock.move'
    
#     def _add_mls_related_to_order(self, related_order_lines, are_qties_done=True):
#         """
#         Override dengan cycle-aware rounding untuk normal dan refund.
#         """
#         res = super()._add_mls_related_to_order(related_order_lines, are_qties_done)
        
#         import logging
#         _logger = logging.getLogger(__name__)
        
#         for move in self:
#             product = move.product_id
#             product_uom = product.uom_id
            
#             pos_lines = related_order_lines.filtered(lambda l: l.product_id == product)
#             if not pos_lines:
#                 continue
            
#             # Deteksi apakah ini refund (return) atau normal sale
#             is_refund = move.location_id.usage == 'customer' and move.location_dest_id.usage == 'internal'
            
#             # --- PRODUK TANPA TRACKING ---
#             if product.tracking == 'none' or (not move.picking_type_id.use_existing_lots and not move.picking_type_id.use_create_lots):
#                 total_qty_raw = 0.0
#                 for line in pos_lines:
#                     line_uom = getattr(line, 'product_uom', False) or getattr(line, 'product_uom_id', False) or product_uom
#                     if line_uom != product_uom:
#                         qty_converted = abs(line.qty) * line_uom.factor_inv / product_uom.factor_inv
#                     else:
#                         qty_converted = abs(line.qty)
#                     total_qty_raw += qty_converted
                
#                 # Get destination stock (untuk refund, dest adalah internal stock)
#                 target_location = move.location_dest_id if is_refund else move.location_id
#                 current_stock = self._get_available_quantity_at_location(
#                     product, target_location, product_uom
#                 )
                
#                 total_qty = self._cycle_aware_rounding(
#                     total_qty_raw,
#                     current_stock,
#                     product_uom.rounding,
#                     is_adding=is_refund  # Refund = menambah stock
#                 )
                
#                 final_stock = current_stock + total_qty if is_refund else current_stock - total_qty
#                 _logger.info(f"Product: {product.name}, {'REFUND' if is_refund else 'SALE'}")
#                 _logger.info(f"  Stock: {current_stock:.5f}, Qty raw: {total_qty_raw:.10f}")
#                 _logger.info(f"  Qty final: {total_qty:.5f}, Result stock: {final_stock:.5f}")
                
#                 if are_qties_done:
#                     move.quantity = total_qty
                
#                 if total_qty and abs(move.product_uom_qty - total_qty) > 1e-6:
#                     move.product_uom_qty = total_qty
                
#                 continue
            
#             # --- PRODUK DENGAN TRACKING (SERIAL/LOT) ---
#             if not move.move_line_ids:
#                 continue
            
#             lot_qty_mapping = defaultdict(float)
            
#             for pos_line in pos_lines:
#                 line_uom = getattr(pos_line, 'product_uom', False) or getattr(pos_line, 'product_uom_id', False) or product_uom
                
#                 if line_uom != product_uom:
#                     qty_raw = abs(pos_line.qty) * line_uom.factor_inv / product_uom.factor_inv
#                 else:
#                     qty_raw = abs(pos_line.qty)
                
#                 for pack_lot in pos_line.pack_lot_ids:
#                     if pack_lot.lot_name:
#                         if product.tracking == 'serial':
#                             lot_qty_mapping[pack_lot.lot_name] = 1.0
#                         else:
#                             lot_qty_mapping[pack_lot.lot_name] += qty_raw
            
#             _logger.info(f"=== Processing move {move.id} for product {product.name}, {'REFUND' if is_refund else 'SALE'} ===")
            
#             total_qty = 0.0
            
#             for ml in move.move_line_ids:
#                 lot_name = ml.lot_name or (ml.lot_id.name if ml.lot_id else False)
                
#                 if not lot_name or lot_name not in lot_qty_mapping:
#                     continue
                
#                 qty_raw = lot_qty_mapping[lot_name]
                
#                 # Get stock dari lokasi yang tepat
#                 target_location = move.location_dest_id if is_refund else move.location_id
#                 lot_stock = self._get_lot_quantity_at_location(
#                     product, target_location, lot_name
#                 )
                
#                 qty_for_lot = self._cycle_aware_rounding(
#                     qty_raw,
#                     lot_stock,
#                     product_uom.rounding,
#                     is_adding=is_refund
#                 )
                
#                 final_stock = lot_stock + qty_for_lot if is_refund else lot_stock - qty_for_lot
#                 _logger.info(f"Lot: {lot_name}, Stock: {lot_stock:.5f}, Raw: {qty_raw:.10f}")
#                 _logger.info(f"  Final: {qty_for_lot:.5f}, Result: {final_stock:.5f}")
                
#                 if are_qties_done:
#                     ml.qty_done = qty_for_lot
#                     ml.quantity_product_uom = qty_for_lot
                
#                 total_qty += qty_for_lot
            
#             if total_qty and abs(move.product_uom_qty - total_qty) > 1e-6:
#                 move.product_uom_qty = total_qty
        
#         return res
    
#     def _cycle_aware_rounding(self, qty_raw, current_stock, precision_rounding, is_adding=False):
#         """
#         Cycle-aware rounding dengan support untuk adding (refund) atau subtracting (sale).
        
#         is_adding=False (SALE):
#           Stock 1.00000 - 0.03333 → 0.96667 ✓
#           Stock 0.96667 - 0.03334 → 0.93333 ✓
#           Stock 0.93333 - 0.03333 → 0.90000 ✓
        
#         is_adding=True (REFUND):
#           Stock 0.90000 + 0.03333 → 0.93333 ✓
#           Stock 0.93333 + 0.03334 → 0.96667 ✓
#           Stock 0.96667 + 0.03333 → 1.00000 ✓
#         """
#         import logging
#         _logger = logging.getLogger(__name__)
        
#         qty_base = float_round(qty_raw, precision_rounding=precision_rounding)
        
#         candidates = []
#         for offset in range(-2, 3):
#             candidate = qty_base + (offset * precision_rounding)
#             if candidate > 0:
#                 candidates.append(candidate)
        
#         best_qty = qty_base
#         best_score = float('inf')
        
#         for candidate in candidates:
#             # Hitung hasil stock setelah operasi
#             if is_adding:
#                 resulting_stock = current_stock + candidate  # REFUND: tambah
#             else:
#                 resulting_stock = current_stock - candidate  # SALE: kurang
            
#             resulting_frac = resulting_stock - int(resulting_stock)
            
#             # Normalisasi ke [0, 1)
#             if resulting_frac < 0:
#                 resulting_frac += 1.0
            
#             # Hitung jarak ke angka "bersih"
#             nearest_tenth = round(resulting_frac * 10) / 10.0
#             distance_to_tenth = abs(resulting_frac - nearest_tenth)
            
#             # Jarak ke kelipatan qty_raw (cycle pattern)
#             if qty_raw > 0:
#                 cycle_position = resulting_frac / qty_raw
#                 nearest_cycle = round(cycle_position) * qty_raw
#                 if nearest_cycle >= 1.0:
#                     nearest_cycle -= 1.0
#                 distance_to_cycle = abs(resulting_frac - nearest_cycle)
#             else:
#                 distance_to_cycle = distance_to_tenth
            
#             distance = min(distance_to_tenth, distance_to_cycle)
#             deviation = abs(candidate - qty_raw)
#             score = distance * 1000 + deviation
            
#             _logger.info(f"  Candidate: {candidate:.5f}, Result: {resulting_stock:.5f}, Frac: {resulting_frac:.5f}")
#             _logger.info(f"    Dist: {distance:.8f}, Score: {score:.8f}")
            
#             if score < best_score:
#                 best_score = score
#                 best_qty = candidate
        
#         return best_qty
    
#     def _get_available_quantity_at_location(self, product, location, uom):
#         quants = self.env['stock.quant'].search([
#             ('product_id', '=', product.id),
#             ('location_id', '=', location.id),
#         ])
#         return sum(quants.mapped('quantity'))
    
#     def _get_lot_quantity_at_location(self, product, location, lot_name):
#         lot = self.env['stock.lot'].search([
#             ('product_id', '=', product.id),
#             ('name', '=', lot_name),
#         ], limit=1)
        
#         if not lot:
#             return 0.0
        
#         quants = self.env['stock.quant'].search([
#             ('product_id', '=', product.id),
#             ('location_id', '=', location.id),
#             ('lot_id', '=', lot.id),
#         ])
        
#         return sum(quants.mapped('quantity'))