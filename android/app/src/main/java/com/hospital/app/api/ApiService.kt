package com.hospital.app.api

import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    @POST("auth/api/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @GET("api/appointments")
    suspend fun getAppointments(
        @Header("Authorization") token: String,
        @Query("status") status: String? = null
    ): Response<List<Appointment>>

    @GET("api/profile")
    suspend fun getProfile(@Header("Authorization") token: String): Response<User>

    @GET("api/cases")
    suspend fun getCases(@Header("Authorization") token: String): Response<List<Case>>

    @POST("api/feedback")
    suspend fun submitFeedback(
        @Header("Authorization") token: String,
        @Body request: FeedbackRequest
    ): Response<Unit>
} 