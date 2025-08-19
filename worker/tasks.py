from __future__ import annotations

import io
import logging
import os
from datetime import datetime

import requests
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from worker.celery_app import celery_app

logger = logging.getLogger("tasks")


def _format_money_minor(amount_minor: int) -> str:
	# Convert minor units to major with two decimals, currency INR
	return f"INR {amount_minor / 100:.2f}"


def _invoice_bytes(order_id: int, order_number: str) -> bytes:
	# Lazy import to avoid circulars on worker boot
	from app.db.session import SessionLocal
	from app.models.order import Order, OrderItem

	with SessionLocal() as db:
		order = db.get(Order, order_id)
		if not order:
			raise RuntimeError(f"Order {order_id} not found for invoice generation")
		items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

	buffer = io.BytesIO()
	doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=20 * mm, bottomMargin=20 * mm)
	styles = getSampleStyleSheet()
	story = []

	# Header
	story.append(Paragraph("ArtiCurated", styles["Title"]))
	story.append(Paragraph("Tax Invoice", styles["h2"]))
	story.append(Spacer(1, 6 * mm))

	# Order metadata
	meta_data = [
		["Invoice No:", f"INV-{order_number}"],
		["Order No:", order_number],
		["Order ID:", str(order_id)],
		["Date:", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")],
		["Customer ID:", order.customer_id],
		["Currency:", order.currency],
	]
	meta_table = Table(meta_data, hAlign="LEFT", colWidths=[30 * mm, 120 * mm])
	meta_table.setStyle(
		TableStyle(
			[
				("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
				("FONTSIZE", (0, 0), (-1, -1), 10),
				("BOTTOMPADDING", (0, 0), (-1, -1), 4),
			]
		)
	)
	story.append(meta_table)
	story.append(Spacer(1, 6 * mm))

	# Items table
	data = [["SKU", "Title", "Qty", "Unit Price", "Amount"]]
	total_minor = 0
	for it in items:
		line_minor = it.quantity * it.unit_price_minor
		total_minor += line_minor
		data.append(
			[
				it.sku,
				it.title,
				str(it.quantity),
				_format_money_minor(it.unit_price_minor),
				_format_money_minor(line_minor),
			]
		)

	items_table = Table(data, hAlign="LEFT", colWidths=[25 * mm, 75 * mm, 15 * mm, 30 * mm, 30 * mm])
	items_table.setStyle(
		TableStyle(
			[
				("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
				("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
				("ALIGN", (2, 1), (-1, -1), "RIGHT"),
				("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
				("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
				("FONTSIZE", (0, 0), (-1, -1), 10),
				("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
				("TOPPADDING", (0, 0), (-1, -1), 6),
				("BOTTOMPADDING", (0, 0), (-1, -1), 6),
			]
		)
	)
	story.append(items_table)
	story.append(Spacer(1, 4 * mm))

	# Totals (no tax for simplicity)
	totals = [
		["Subtotal", _format_money_minor(total_minor)],
		["Total", _format_money_minor(total_minor)],
	]
	tot_table = Table(totals, hAlign="RIGHT", colWidths=[30 * mm, 30 * mm])
	tot_table.setStyle(
		TableStyle(
			[
				("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
				("FONTSIZE", (0, 0), (-1, -1), 11),
				("ALIGN", (0, 0), (-1, -1), "RIGHT"),
				("BOTTOMPADDING", (0, 0), (-1, -1), 4),
				("LINEABOVE", (0, 1), (-1, 1), 0.5, colors.black),
				("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
			]
		)
	)
	story.append(tot_table)
	story.append(Spacer(1, 8 * mm))

	# Footer
	story.append(Paragraph("Thank you for shopping with ArtiCurated.", styles["Italic"]))
	story.append(Paragraph("This is a system-generated invoice.", styles["BodyText"]))

	doc.build(story)
	buffer.seek(0)
	return buffer.read()


@celery_app.task(name="generate_invoice_and_email")
def generate_invoice_and_email(order_id: int, order_number: str) -> str:
	invoice_dir = os.getenv("INVOICE_OUTPUT_DIR", "/tmp/invoices")
	os.makedirs(invoice_dir, exist_ok=True)
	pdf_bytes = _invoice_bytes(order_id, order_number)
	pdf_path = os.path.join(invoice_dir, f"invoice_{order_number}.pdf")
	with open(pdf_path, "wb") as f:
		f.write(pdf_bytes)
	logger.info("Generated invoice %s; emailing to customer (simulated)", pdf_path)
	return pdf_path


@celery_app.task(name="process_refund")
def process_refund(return_id: int, amount_minor: int, currency: str = "INR") -> dict:
	base = os.getenv("PAYMENT_GATEWAY_BASE_URL", "http://payment-gateway:9000")
	url = f"{base}/refund"
	payload = {"return_id": str(return_id), "amount": int(amount_minor), "currency": currency}
	resp = requests.post(url, json=payload, timeout=5)
	resp.raise_for_status()
	logger.info("Refund requested for return_id=%s amount=%s %s", return_id, amount_minor, currency)
	return resp.json()
