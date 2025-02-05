package com.hospital.app.ui.appointments

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.hospital.app.api.ApiService
import com.hospital.app.api.RetrofitClient
import com.hospital.app.api.Appointment
import kotlinx.coroutines.launch
import retrofit2.Response
import java.net.UnknownHostException

class AppointmentsViewModel : ViewModel() {
    private val apiService: ApiService = RetrofitClient.apiService

    private val _appointments = MutableLiveData<List<Appointment>>()
    val appointments: LiveData<List<Appointment>> = _appointments

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun loadAppointments(token: String?, status: String? = null) {
        if (token == null) {
            _error.value = "Authentication token not found"
            return
        }

        viewModelScope.launch {
            try {
                _isLoading.value = true
                _error.value = null
                
                val response: Response<List<Appointment>> = apiService.getAppointments(
                    token = "Bearer $token",
                    status = status
                )
                
                if (response.isSuccessful) {
                    val appointments = response.body() ?: emptyList()
                    _appointments.value = appointments.sortedByDescending { it.datetime }
                } else {
                    when (response.code()) {
                        401 -> _error.value = "Session expired. Please login again."
                        403 -> _error.value = "You don't have permission to view appointments."
                        404 -> {
                            _error.value = "No appointments found"
                            _appointments.value = emptyList()
                        }
                        else -> _error.value = "Failed to load appointments: ${response.message()}"
                    }
                }
            } catch (e: UnknownHostException) {
                _error.value = "No internet connection. Please check your network."
            } catch (e: Exception) {
                _error.value = "Error: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun filterAppointments(status: String?, token: String?) {
        loadAppointments(token, status)
    }
} 