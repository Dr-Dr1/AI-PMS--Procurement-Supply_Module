# Procurement & Supply Chain API Documentation

Base URL: `/api/v1/procurement`

## Dashboard

### 1. Get Procurement Dashboard Summary
- **Endpoint**: `GET /dashboard/summary`
- **Description**: Aggregated metrics: PO counts by status, vendor stats, pending deliveries, upcoming FATs, total procurement value.
- **Request**: None
- **Response**: `ProcurementDashboard`
```json
{
  "total_purchase_orders": 0,
  "po_by_status": {},
  "total_vendors": 0,
  "active_vendors": 0,
  "total_materials": 0,
  "pending_deliveries": 0,
  "upcoming_fat_tests": 0,
  "total_procurement_value": 0.00
}
```

---

## Vendors

### 2. Register Vendor
- **Endpoint**: `POST /vendors`
- **Description**: Register a new vendor/supplier in the system.
- **Request**: `VendorCreate`
```json
{
  "name": "string (max 300)",
  "code": "string (max 50)",
  "contact_email": "string (max 255, optional)",
  "contact_phone": "string (max 20, optional)",
  "address": "string (optional)",
  "gst_number": "string (max 20, optional)",
  "pan_number": "string (max 15, optional)"
}
```
- **Response**: `VendorResponse`

### 3. List Vendors
- **Endpoint**: `GET /vendors`
- **Description**: Paginated vendor listing with optional filters.
- **Query Parameters**:
  - `page` (int, default=1)
  - `page_size` (int, default=20)
  - `status` (string, optional)
  - `is_active` (boolean, optional)
- **Request**: None
- **Response**: `PaginatedResponse` containing list of `VendorListResponse`

### 4. Get Vendor
- **Endpoint**: `GET /vendors/{vendor_id}`
- **Description**: Retrieve a single vendor by ID.
- **Request**: None
- **Response**: `VendorResponse`

### 5. Update Vendor
- **Endpoint**: `PUT /vendors/{vendor_id}`
- **Description**: Update vendor details. Only provided fields are modified.
- **Request**: `VendorUpdate`
```json
{
  "name": "string (optional)",
  "contact_email": "string (optional)",
  "contact_phone": "string (optional)",
  "address": "string (optional)",
  "gst_number": "string (optional)",
  "pan_number": "string (optional)",
  "vendor_status": "string (optional)",
  "vendor_tier": "string (optional)"
}
```
- **Response**: `VendorResponse`

### 6. Add Vendor Score
- **Endpoint**: `POST /vendors/{vendor_id}/scores`
- **Description**: Record a periodic performance score. Overall score is auto-calculated using weighted formula.
- **Request**: `VendorScoreCreate`
```json
{
  "scoring_period": "string",
  "quality_score": 0.00,
  "delivery_score": 0.00,
  "compliance_score": 0.00,
  "price_score": 0.00,
  "remarks": "string (optional)"
}
```
- **Response**: `VendorScoreResponse`

### 7. Vendor Score History
- **Endpoint**: `GET /vendors/{vendor_id}/scores`
- **Description**: Retrieve historical performance scores for a vendor.
- **Query Parameters**: `page`, `page_size`
- **Request**: None
- **Response**: List of `VendorScoreResponse`

---

## Materials

### 8. Create Material
- **Endpoint**: `POST /materials`
- **Description**: Add a new material to the catalogue.
- **Request**: `MaterialCreate`
```json
{
  "name": "string (max 300)",
  "code": "string (max 50)",
  "description": "string (optional)",
  "category": "string",
  "unit": "string (max 30)",
  "hsn_code": "string (max 20, optional)",
  "specifications": {}
}
```
- **Response**: `MaterialResponse`

### 9. List Materials
- **Endpoint**: `GET /materials`
- **Description**: Paginated material catalogue with optional category filter.
- **Query Parameters**: `page`, `page_size`, `category`, `is_active`
- **Request**: None
- **Response**: `PaginatedResponse` containing `MaterialResponse`

### 10. Get Material
- **Endpoint**: `GET /materials/{material_id}`
- **Description**: Retrieve a single material by ID.
- **Request**: None
- **Response**: `MaterialResponse`

### 11. Update Material
- **Endpoint**: `PUT /materials/{material_id}`
- **Description**: Update material details. Only provided fields are modified.
- **Request**: `MaterialUpdate`
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "category": "string (optional)",
  "unit": "string (optional)",
  "hsn_code": "string (optional)",
  "specifications": {},
  "is_active": true
}
```
- **Response**: `MaterialResponse`

---

## Purchase Orders

### 12. Create Purchase Order
- **Endpoint**: `POST /purchase-orders`
- **Description**: Create a new PO with line items. Total value is auto-calculated.
- **Request**: `PurchaseOrderCreate`
```json
{
  "po_number": "string",
  "vendor_id": "uuid",
  "package_id": "uuid (optional)",
  "title": "string",
  "description": "string (optional)",
  "currency": "INR",
  "delivery_address": "string (optional)",
  "expected_delivery_date": "YYYY-MM-DD (optional)",
  "terms_and_conditions": "string (optional)",
  "remarks": "string (optional)",
  "line_items": [
    {
      "material_id": "uuid",
      "description": "string (optional)",
      "quantity": 0.00,
      "unit_price": 0.00,
      "unit": "string"
    }
  ]
}
```
- **Response**: `PurchaseOrderResponse`

### 13. List Purchase Orders
- **Endpoint**: `GET /purchase-orders`
- **Description**: Paginated PO listing with optional status and vendor filters.
- **Query Parameters**: `page`, `page_size`, `status`, `vendor_id`
- **Request**: None
- **Response**: `PaginatedResponse` containing `PurchaseOrderListResponse`

### 14. Get Purchase Order
- **Endpoint**: `GET /purchase-orders/{po_id}`
- **Description**: Retrieve a single PO with all line items.
- **Request**: None
- **Response**: `PurchaseOrderResponse`

### 15. Update Purchase Order
- **Endpoint**: `PUT /purchase-orders/{po_id}`
- **Description**: Update PO details. Only allowed when PO is in DRAFT status.
- **Request**: `PurchaseOrderUpdate`
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "delivery_address": "string (optional)",
  "expected_delivery_date": "YYYY-MM-DD (optional)",
  "terms_and_conditions": "string (optional)",
  "remarks": "string (optional)"
}
```
- **Response**: `PurchaseOrderResponse`

### 16. Update PO Status
- **Endpoint**: `PATCH /purchase-orders/{po_id}/status`
- **Description**: Transition PO to a new status according to state machine.
- **Request**: `StatusUpdate`
```json
{
  "status": "string",
  "remarks": "string (optional)"
}
```
- **Response**: `PurchaseOrderResponse`

---

## Deliveries

### 17. Create Delivery
- **Endpoint**: `POST /deliveries`
- **Description**: Record a new delivery/shipment against a purchase order.
- **Request**: `DeliveryCreate`
```json
{
  "po_id": "uuid",
  "delivery_number": "string",
  "dispatch_date": "YYYY-MM-DD (optional)",
  "expected_arrival": "YYYY-MM-DD (optional)",
  "transporter_name": "string (optional)",
  "tracking_number": "string (optional)",
  "remarks": "string (optional)",
  "items": [
    {
      "po_line_item_id": "uuid",
      "delivered_quantity": 0.00,
      "accepted_quantity": 0.00,
      "rejected_quantity": 0.00,
      "rejection_reason": "string (optional)"
    }
  ]
}
```
- **Response**: `DeliveryResponse`

### 18. List Deliveries
- **Endpoint**: `GET /deliveries`
- **Description**: Paginated delivery listing with optional PO and status filters.
- **Query Parameters**: `page`, `page_size`, `po_id`, `status`
- **Request**: None
- **Response**: `PaginatedResponse` containing `DeliveryResponse`

### 19. Get Delivery
- **Endpoint**: `GET /deliveries/{delivery_id}`
- **Description**: Retrieve a single delivery with all line items.
- **Request**: None
- **Response**: `DeliveryResponse`

### 20. Update Delivery
- **Endpoint**: `PUT /deliveries/{delivery_id}`
- **Description**: Update delivery details (dates, transporter, tracking).
- **Request**: `DeliveryUpdate`
```json
{
  "dispatch_date": "YYYY-MM-DD (optional)",
  "expected_arrival": "YYYY-MM-DD (optional)",
  "actual_arrival": "YYYY-MM-DD (optional)",
  "transporter_name": "string (optional)",
  "tracking_number": "string (optional)",
  "remarks": "string (optional)"
}
```
- **Response**: `DeliveryResponse`

### 21. Update Delivery Status
- **Endpoint**: `PATCH /deliveries/{delivery_id}/status`
- **Description**: Transition delivery status.
- **Request**: `StatusUpdate`
- **Response**: `DeliveryResponse`

---

## FAT Tests (Factory Acceptance Testing)

### 22. Schedule FAT Test
- **Endpoint**: `POST /fat-tests`
- **Description**: Schedule a Factory Acceptance Test for a PO/vendor.
- **Request**: `FATTestCreate`
```json
{
  "po_id": "uuid",
  "vendor_id": "uuid",
  "test_number": "string",
  "scheduled_date": "YYYY-MM-DD",
  "inspector_name": "string (optional)",
  "inspector_id": "uuid (optional)",
  "test_location": "string (optional)",
  "remarks": "string (optional)"
}
```
- **Response**: `FATTestResponse`

### 23. List FAT Tests
- **Endpoint**: `GET /fat-tests`
- **Description**: Paginated FAT listing with optional PO, vendor, and status filters.
- **Query Parameters**: `page`, `page_size`, `po_id`, `vendor_id`, `status`
- **Request**: None
- **Response**: `PaginatedResponse` containing `FATTestResponse`

### 24. Get FAT Test
- **Endpoint**: `GET /fat-tests/{fat_id}`
- **Description**: Retrieve a single FAT test by ID.
- **Request**: None
- **Response**: `FATTestResponse`

### 25. Update FAT Test
- **Endpoint**: `PUT /fat-tests/{fat_id}`
- **Description**: Update FAT test details (dates, inspector, location, report URL).
- **Request**: `FATTestUpdate`
```json
{
  "scheduled_date": "YYYY-MM-DD (optional)",
  "actual_date": "YYYY-MM-DD (optional)",
  "inspector_name": "string (optional)",
  "inspector_id": "uuid (optional)",
  "test_location": "string (optional)",
  "test_report_url": "string (optional)",
  "result_summary": "string (optional)",
  "remarks": "string (optional)"
}
```
- **Response**: `FATTestResponse`

### 26. Update FAT Status
- **Endpoint**: `PATCH /fat-tests/{fat_id}/status`
- **Description**: Transition FAT status.
- **Request**: `StatusUpdate`
- **Response**: `FATTestResponse`
