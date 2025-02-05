package com.hospital.app.api

import android.util.Log
import com.google.gson.GsonBuilder
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {
    private const val TAG = "RetrofitClient"
    private const val BASE_URL = "http://192.168.1.6:5000/"  // Updated server IP

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val gson = GsonBuilder()
        .setLenient()
        .registerTypeAdapter(List::class.java, ListTypeAdapter())
        .create()

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .addInterceptor { chain ->
            val originalRequest = chain.request()
            
            // Log the complete URL and headers for debugging
            Log.d(TAG, "Making request to: ${originalRequest.url}")
            
            // Log headers safely
            val headers = originalRequest.headers
            for (i in 0 until headers.size) {
                val name = headers.name(i)
                if (name == "Authorization") {
                    Log.d(TAG, "Authorization header present")
                } else {
                    Log.d(TAG, "Header: $name = ${headers.value(i)}")
                }
            }
            
            val request = originalRequest.newBuilder()
                .header("Accept", "application/json")
                .header("Content-Type", "application/json")
                .build()
            
            try {
                val response = chain.proceed(request)
                Log.d(TAG, "Response Code: ${response.code}")
                
                if (!response.isSuccessful) {
                    val errorBody = response.body?.string()
                    Log.e(TAG, "Error Response: $errorBody")
                    Log.e(TAG, "Error Response Headers: ${response.headers}")
                    Log.e(TAG, "Failed URL: ${response.request.url}")
                } else {
                    val responseBody = response.peekBody(Long.MAX_VALUE).string()
                    Log.d(TAG, "Success Response: $responseBody")
                }
                
                response
            } catch (e: Exception) {
                Log.e(TAG, "Network Error: ${e.message}")
                Log.e(TAG, "Failed URL: ${originalRequest.url}")
                Log.e(TAG, "Stack Trace: ", e)
                throw e
            }
        }
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create(gson))
        .build()

    val apiService: ApiService = retrofit.create(ApiService::class.java)
} 