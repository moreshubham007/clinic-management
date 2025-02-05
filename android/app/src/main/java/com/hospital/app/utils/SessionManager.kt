package com.hospital.app.utils

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SessionManager(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val sharedPreferences: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    companion object {
        const val USER_TOKEN = "user_token"
        const val USER_ID = "user_id"
        const val USER_NAME = "user_name"
        const val USER_EMAIL = "user_email"
        const val PATIENT_NUMBER = "patient_number"
        private const val KEY_TOKEN = "token"
    }

    fun saveToken(token: String) {
        sharedPreferences.edit().putString(KEY_TOKEN, token).apply()
    }

    fun getToken(): String? {
        return sharedPreferences.getString(KEY_TOKEN, null)
    }

    fun saveUserInfo(id: Int, name: String, email: String, patientNumber: String?) {
        val editor = sharedPreferences.edit()
        editor.putInt(USER_ID, id)
        editor.putString(USER_NAME, name)
        editor.putString(USER_EMAIL, email)
        editor.putString(PATIENT_NUMBER, patientNumber)
        editor.apply()
    }

    fun clearSession() {
        sharedPreferences.edit().clear().apply()
    }
} 