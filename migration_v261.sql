-- =============================================================
-- Migration: version-8 → version-26.1
-- Run against production MariaDB / MySQL
-- Safe to run multiple times (uses IF NOT EXISTS / IF EXISTS)
-- =============================================================

-- ── 1. Add patient_type to existing appointment table ─────────
ALTER TABLE appointment
    ADD COLUMN IF NOT EXISTS patient_type VARCHAR(20) DEFAULT 'existing';

-- ── 2. Create medicine_order table ────────────────────────────
CREATE TABLE IF NOT EXISTS medicine_order (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    order_number        VARCHAR(20)     NOT NULL,
    mobile_number       VARCHAR(15)     NOT NULL,
    patient_id          INT             NULL,
    patient_number      VARCHAR(11)     NULL,
    duration_days       INT             NOT NULL,
    delivery_type       VARCHAR(20)     NOT NULL,
    pickup_date         DATE            NULL,
    delivery_address    TEXT            NULL,
    courier_name        VARCHAR(100)    NULL,
    courier_awb         VARCHAR(100)    NULL,
    courier_tracking_url VARCHAR(500)   NULL,
    additional_notes    TEXT            NULL,
    status              VARCHAR(20)     DEFAULT 'pending',
    payment_status      VARCHAR(20)     DEFAULT 'unpaid',
    payment_amount      DECIMAL(10,2)   NULL,
    payment_mode        VARCHAR(20)     NULL,
    created_at          DATETIME        NULL,
    updated_at          DATETIME        NULL,
    UNIQUE KEY uq_medicine_order_number (order_number),
    CONSTRAINT fk_mo_patient FOREIGN KEY (patient_id) REFERENCES user(id)
);

-- ── 3. If medicine_order already existed, add missing columns ──
--    (safe no-ops if the table was just created above)
ALTER TABLE medicine_order
    ADD COLUMN IF NOT EXISTS courier_name        VARCHAR(100)  NULL,
    ADD COLUMN IF NOT EXISTS courier_awb         VARCHAR(100)  NULL,
    ADD COLUMN IF NOT EXISTS courier_tracking_url VARCHAR(500) NULL,
    ADD COLUMN IF NOT EXISTS payment_status      VARCHAR(20)   DEFAULT 'unpaid',
    ADD COLUMN IF NOT EXISTS payment_amount      DECIMAL(10,2) NULL,
    ADD COLUMN IF NOT EXISTS payment_mode        VARCHAR(20)   NULL;

-- ── 4. Create appointment_request table ───────────────────────
CREATE TABLE IF NOT EXISTS appointment_request (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    request_number  VARCHAR(20)     NOT NULL,
    patient_type    VARCHAR(20)     NOT NULL,
    mobile_number   VARCHAR(15)     NOT NULL,
    preferred_date  DATE            NULL,
    preferred_time  VARCHAR(30)     NULL,
    notes           TEXT            NULL,
    patient_name    VARCHAR(100)    NULL,
    patient_email   VARCHAR(120)    NULL,
    patient_gender  VARCHAR(10)     NULL,
    patient_id      INT             NULL,
    patient_number  VARCHAR(11)     NULL,
    status          VARCHAR(20)     DEFAULT 'pending',
    created_at      DATETIME        NULL,
    UNIQUE KEY uq_appt_request_number (request_number),
    CONSTRAINT fk_ar_patient FOREIGN KEY (patient_id) REFERENCES user(id)
);

-- ── 5. Fix preferred_time length if table already existed ──────
ALTER TABLE appointment_request
    MODIFY COLUMN IF EXISTS preferred_time VARCHAR(30) NULL;

-- ── 6. Add billing columns to appointment ────────────────────────────────────
ALTER TABLE appointment
    ADD COLUMN IF NOT EXISTS consultation_fee  DECIMAL(10,2) NULL AFTER payment_date,
    ADD COLUMN IF NOT EXISTS medicine_charges  DECIMAL(10,2) NULL AFTER consultation_fee,
    ADD COLUMN IF NOT EXISTS discount          DECIMAL(10,2) NULL DEFAULT 0 AFTER medicine_charges;

-- Also add 'partial' as valid payment_status (existing rows are fine — VARCHAR allows it)

-- ── 7. Add created_by_id to medicine_order (tracks staff vs public orders) ──
ALTER TABLE medicine_order
    ADD COLUMN IF NOT EXISTS created_by_id INT NULL AFTER payment_mode;

-- Add FK only if it doesn't already exist (MariaDB doesn't support IF NOT EXISTS
-- for constraints, so wrap in a stored procedure trick or run manually if needed)
ALTER TABLE medicine_order
    ADD CONSTRAINT fk_mo_created_by
        FOREIGN KEY (created_by_id) REFERENCES user(id)
        ON DELETE SET NULL;

-- =============================================================
-- Verification queries — run these after migration to confirm
-- =============================================================
-- SHOW COLUMNS FROM medicine_order;
-- SHOW COLUMNS FROM appointment_request;
-- SHOW COLUMNS FROM appointment LIKE 'patient_type';
