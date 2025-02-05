package com.hospital.app.ui.auth

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.hospital.app.api.LoginRequest
import com.hospital.app.api.RetrofitClient
import kotlinx.coroutines.launch

sealed class LoginResult {
    object Loading : LoginResult()
    data class Success(
        val token: String,
        val userId: Int,
        val name: String,
        val email: String,
        val patientNumber: String?
    ) : LoginResult()
    data class Error(val message: String) : LoginResult()
}

class LoginViewModel : ViewModel() {
    private val _loginResult = MutableLiveData<LoginResult>()
    val loginResult: LiveData<LoginResult> = _loginResult

    fun login(email: String, password: String) {
        viewModelScope.launch {
            try {
                _loginResult.value = LoginResult.Loading
                val response = RetrofitClient.apiService.login(LoginRequest(email, password))

                if (response.isSuccessful) {
                    val loginResponse = response.body()
                    if (loginResponse != null) {
                        _loginResult.value = LoginResult.Success(
                            token = loginResponse.token,
                            userId = loginResponse.user.id,
                            name = loginResponse.user.name,
                            email = loginResponse.user.email,
                            patientNumber = loginResponse.user.patient_number
                        )
                    } else {
                        _loginResult.value = LoginResult.Error("Invalid response from server")
                    }
                } else {
                    _loginResult.value = LoginResult.Error(response.message() ?: "Login failed")
                }
            } catch (e: Exception) {
                _loginResult.value = LoginResult.Error(e.message ?: "Unknown error occurred")
            }
        }
    }
} 