package com.hospital.app.api

data class LoginRequest(
    val email: String,
    val password: String
)

data class LoginResponse(
    val token: String,
    val user: User
)

data class User(
    val id: Int,
    val name: String,
    val email: String,
    val patient_number: String?
)

data class Doctor(
    val id: Int,
    val name: String,
    val specialization: String
)

data class Appointment(
    val id: Int,
    val datetime: String,
    val status: String,
    val doctor: Doctor,
    val notes: String?
)

data class Case(
    val id: Int,
    val created_at: String,
    val doctor: Doctor,
    val diagnosis: String?,
    val treatment: String?,
    val status: String
)

data class FeedbackRequest(
    val doctor_id: Int,
    val rating: Int,
    val comment: String?,
    val is_anonymous: Boolean = false
) 