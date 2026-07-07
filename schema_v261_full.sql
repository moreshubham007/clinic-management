-- =============================================================
-- FULL DATABASE SCHEMA — Clinic Management System v26.1
-- Fresh deployment (new server / new database)
-- =============================================================
-- Usage:
--   docker exec -i mariadb-clinic mariadb -uhospital -phospital123 clinic_db \
--     < schema_v261_full.sql
-- =============================================================

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';

-- ── 1. user ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user (
    id              INT             AUTO_INCREMENT PRIMARY KEY,
    email           VARCHAR(120)    NOT NULL,
    password_hash   VARCHAR(256)    NULL,
    name            VARCHAR(100)    NOT NULL,
    role            VARCHAR(20)     NOT NULL,          -- admin / receptionist / doctor / patient
    google_id       VARCHAR(100)    NULL,
    is_active       TINYINT(1)      DEFAULT 1,
    created_at      DATETIME        NULL,
    -- Patient-specific
    address         TEXT            NULL,
    state           VARCHAR(50)     NULL,
    city            VARCHAR(50)     NULL,
    pin_code        VARCHAR(6)      NULL,
    mobile_number   VARCHAR(15)     NULL,
    date_of_birth   DATE            NULL,
    aadhar_number   VARCHAR(12)     NULL,
    patient_number  VARCHAR(11)     NULL,
    gender          VARCHAR(10)     NULL,
    UNIQUE KEY uq_user_email         (email),
    UNIQUE KEY uq_user_google_id     (google_id),
    UNIQUE KEY uq_user_aadhar        (aadhar_number),
    UNIQUE KEY uq_user_patient_number(patient_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── 2. doctor ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS doctor (
    id              INT             AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL,
    specialization  VARCHAR(100)    NULL,
    availability    JSON            NULL,
    CONSTRAINT fk_doctor_user FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── 3. appointment ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS appointment (
    id                  INT             AUTO_INCREMENT PRIMARY KEY,
    doctor_id           INT             NOT NULL,
    patient_id          INT             NOT NULL,
    datetime            DATETIME        NOT NULL,
    status              VARCHAR(20)     DEFAULT 'scheduled',
    patient_type        VARCHAR(20)     DEFAULT 'existing',
    priority            VARCHAR(10)     DEFAULT 'medium',    -- high / medium / low
    notes               TEXT            NULL,
    remarks             TEXT            NULL,
    payment_status      VARCHAR(20)     DEFAULT 'unpaid',    -- paid / unpaid
    payment_amount      DOUBLE          NULL,
    payment_mode        VARCHAR(20)     NULL,                -- cash / online
    payment_received_by INT             NULL,
    payment_date        DATETIME        NULL,
    created_at          DATETIME        NULL,
    updated_at          DATETIME        NULL,
    CONSTRAINT fk_appt_doctor           FOREIGN KEY (doctor_id)           REFERENCES doctor(id),
    CONSTRAINT fk_appt_patient          FOREIGN KEY (patient_id)          REFERENCES user(id),
    CONSTRAINT fk_appt_payment_recv     FOREIGN KEY (payment_received_by) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── 4. case ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `case` (
    id              INT             AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT             NOT NULL,
    doctor_id       INT             NOT NULL,
    diagnosis       TEXT            NULL,
    treatment       TEXT            NULL,
    created_at      DATETIME        NULL,
    updated_at      DATETIME        NULL,
    show_to_patient TINYINT(1)      DEFAULT 0,
    status          VARCHAR(20)     DEFAULT 'active',        -- active / closed / transferred
    CONSTRAINT fk_case_patient FOREIGN KEY (patient_id) REFERENCES user(id),
    CONSTRAINT fk_case_doctor  FOREIGN KEY (doctor_id)  REFERENCES doctor(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── 5. case_history ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS case_history (
    id          INT         AUTO_INCREMENT PRIMARY KEY,
    case_id     INT         NOT NULL,
    doctor_id   INT         NOT NULL,
    notes       TEXT        NULL,
    created_at  DATETIME    NULL,
    CONSTRAINT fk_ch_case   FOREIGN KEY (case_id)   REFERENCES `case`(id),
    CONSTRAINT fk_ch_doctor FOREIGN KEY (doctor_id) REFERENCES doctor(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── 6. case_attachment ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS case_attachment (
    id                  INT             AUTO_INCREMENT PRIMARY KEY,
    case_id             INT             NOT NULL,
    filename            VARCHAR(255)    NOT NULL,
    original_filename   VARCHAR(255)    NOT NULL,
    file_type           VARCHAR(50)     NOT NULL,
    file_size           INT             NOT NULL,
    uploaded_at         DATETIME        NULL,
    uploaded_by_id      INT             NOT NULL,
    CONSTRAINT fk_ca_case     FOREIGN KEY (case_id)        REFERENCES `case`(id) ON DELETE CASCADE,
    CONSTRAINT fk_ca_uploader FOREIGN KEY (uploaded_by_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── 7. case_transfer ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS case_transfer (
    id                  INT             AUTO_INCREMENT PRIMARY KEY,
    case_id             INT             NOT NULL,
    from_doctor_id      INT             NOT NULL,
    to_doctor_id        INT             NOT NULL,
    patient_id          INT             NOT NULL,
    transfer_reason     TEXT            NULL,
    transfer_notes      TEXT            NULL,
    patient_condition   TEXT            NULL,
    patient_history     TEXT            NULL,
    current_medications TEXT            NULL,
    transfer_priority   VARCHAR(20)     NULL,               -- urgent / normal / low
    status              VARCHAR(20)     DEFAULT 'pending',  -- pending / accepted / rejected
    created_at          DATETIME        NULL,
    updated_at          DATETIME        NULL,
    CONSTRAINT fk_ct_case        FOREIGN KEY (case_id)        REFERENCES `case`(id),
    CONSTRAINT fk_ct_from_doctor FOREIGN KEY (from_doctor_id) REFERENCES doctor(id),
    CONSTRAINT fk_ct_to_doctor   FOREIGN KEY (to_doctor_id)   REFERENCES doctor(id),
    CONSTRAINT fk_ct_patient     FOREIGN KEY (patient_id)     REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── 8. question ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS question (
    id          INT         AUTO_INCREMENT PRIMARY KEY,
    patient_id  INT         NOT NULL,
    doctor_id   INT         NOT NULL,
    question    TEXT        NULL,
    answer      TEXT        NULL,
    created_at  DATETIME    NULL,
    answered_at DATETIME    NULL,
    is_private  TINYINT(1)  DEFAULT 0,
    CONSTRAINT fk_q_patient FOREIGN KEY (patient_id) REFERENCES user(id),
    CONSTRAINT fk_q_doctor  FOREIGN KEY (doctor_id)  REFERENCES doctor(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── 9. feedback ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS feedback (
    id           INT         AUTO_INCREMENT PRIMARY KEY,
    patient_id   INT         NOT NULL,
    doctor_id    INT         NOT NULL,
    rating       INT         NULL,                          -- 1-5
    comment      TEXT        NULL,
    created_at   DATETIME    NULL,
    is_anonymous TINYINT(1)  DEFAULT 0,
    CONSTRAINT fk_fb_patient FOREIGN KEY (patient_id) REFERENCES user(id),
    CONSTRAINT fk_fb_doctor  FOREIGN KEY (doctor_id)  REFERENCES doctor(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── 10. waiting_area ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS waiting_area (
    id                          INT         AUTO_INCREMENT PRIMARY KEY,
    appointment_id              INT         NOT NULL,
    patient_id                  INT         NOT NULL,
    doctor_id                   INT         NOT NULL,
    check_in_time               DATETIME    NULL,
    expected_appointment_time   DATETIME    NOT NULL,
    actual_start_time           DATETIME    NULL,
    completion_time             DATETIME    NULL,
    status                      VARCHAR(20) DEFAULT 'waiting',  -- waiting / in_progress / completed / cancelled
    priority                    VARCHAR(10) DEFAULT 'normal',   -- urgent / high / normal / low
    notes                       TEXT        NULL,
    doctor_notes                TEXT        NULL,
    wait_time_minutes           INT         NULL,
    added_by_id                 INT         NOT NULL,
    created_at                  DATETIME    NULL,
    updated_at                  DATETIME    NULL,
    CONSTRAINT fk_wa_appointment FOREIGN KEY (appointment_id) REFERENCES appointment(id),
    CONSTRAINT fk_wa_patient     FOREIGN KEY (patient_id)     REFERENCES user(id),
    CONSTRAINT fk_wa_doctor      FOREIGN KEY (doctor_id)      REFERENCES doctor(id),
    CONSTRAINT fk_wa_added_by    FOREIGN KEY (added_by_id)    REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── 11. medicine_order ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS medicine_order (
    id                   INT             AUTO_INCREMENT PRIMARY KEY,
    order_number         VARCHAR(20)     NOT NULL,
    mobile_number        VARCHAR(15)     NOT NULL,
    patient_id           INT             NULL,
    patient_number       VARCHAR(11)     NULL,
    duration_days        INT             NOT NULL,
    delivery_type        VARCHAR(20)     NOT NULL,          -- self_pickup / courier
    pickup_date          DATE            NULL,
    delivery_address     TEXT            NULL,
    courier_name         VARCHAR(100)    NULL,
    courier_awb          VARCHAR(100)    NULL,
    courier_tracking_url VARCHAR(500)    NULL,
    additional_notes     TEXT            NULL,
    status               VARCHAR(20)     DEFAULT 'pending', -- pending/processing/ready/delivered/cancelled
    payment_status       VARCHAR(20)     DEFAULT 'unpaid',  -- unpaid / paid
    payment_amount       DECIMAL(10,2)   NULL,
    payment_mode         VARCHAR(20)     NULL,              -- Cash/Online/UPI/Card/NEFT/RTGS
    created_at           DATETIME        NULL,
    updated_at           DATETIME        NULL,
    UNIQUE KEY uq_medicine_order_number (order_number),
    CONSTRAINT fk_mo_patient FOREIGN KEY (patient_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── 12. appointment_request ───────────────────────────────────
CREATE TABLE IF NOT EXISTS appointment_request (
    id              INT             AUTO_INCREMENT PRIMARY KEY,
    request_number  VARCHAR(20)     NOT NULL,
    patient_type    VARCHAR(20)     NOT NULL,               -- new / existing
    mobile_number   VARCHAR(15)     NOT NULL,
    preferred_date  DATE            NULL,
    preferred_time  VARCHAR(30)     NULL,
    notes           TEXT            NULL,
    patient_name    VARCHAR(100)    NULL,
    patient_email   VARCHAR(120)    NULL,
    patient_gender  VARCHAR(10)     NULL,
    patient_id      INT             NULL,
    patient_number  VARCHAR(11)     NULL,
    status          VARCHAR(20)     DEFAULT 'pending',      -- pending / confirmed / cancelled
    created_at      DATETIME        NULL,
    UNIQUE KEY uq_appt_request_number (request_number),
    CONSTRAINT fk_ar_patient FOREIGN KEY (patient_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


SET FOREIGN_KEY_CHECKS = 1;

-- =============================================================
-- Default admin user  (change password after first login!)
-- password = admin123  (bcrypt hash below)
-- =============================================================
INSERT IGNORE INTO user (email, password_hash, name, role, is_active, created_at)
VALUES (
    'admin@clinic.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhN4LuM3SE5A7sT5qlme2e',
    'Administrator',
    'admin',
    1,
    NOW()
);

-- =============================================================
-- Verify all tables created:
-- SHOW TABLES;
-- =============================================================
