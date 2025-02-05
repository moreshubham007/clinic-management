package com.hospital.app.ui.profile

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.hospital.app.api.ApiService
import com.hospital.app.api.RetrofitClient
import com.hospital.app.api.User
import kotlinx.coroutines.launch
import retrofit2.Response

class ProfileViewModel : ViewModel() {
    private val apiService: ApiService = RetrofitClient.apiService

    private val _profile = MutableLiveData<User>()
    val profile: LiveData<User> = _profile

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    fun loadProfile(token: String?) {
        if (token == null) {
            _error.value = "Authentication token not found"
            return
        }

        viewModelScope.launch {
            try {
                _isLoading.value = true
                val response: Response<User> = apiService.getProfile("Bearer $token")
                
                if (response.isSuccessful) {
                    _profile.value = response.body()
                } else {
                    _error.value = "Failed to load profile: ${response.message()}"
                }
            } catch (e: Exception) {
                _error.value = "Error: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }
} 