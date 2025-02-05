package com.hospital.app.ui.cases

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.hospital.app.api.ApiService
import com.hospital.app.api.RetrofitClient
import com.hospital.app.api.Case
import kotlinx.coroutines.launch
import retrofit2.Response

class CasesViewModel : ViewModel() {
    private val apiService: ApiService = RetrofitClient.apiService

    private val _cases = MutableLiveData<List<Case>>()
    val cases: LiveData<List<Case>> = _cases

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    fun loadCases(token: String?) {
        if (token == null) {
            _error.value = "Authentication token not found"
            return
        }

        viewModelScope.launch {
            try {
                _isLoading.value = true
                val response: Response<List<Case>> = apiService.getCases("Bearer $token")
                
                if (response.isSuccessful) {
                    _cases.value = response.body() ?: emptyList()
                } else {
                    _error.value = "Failed to load cases: ${response.message()}"
                }
            } catch (e: Exception) {
                _error.value = "Error: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }
} 