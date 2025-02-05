package com.hospital.app.ui.auth

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import com.hospital.app.databinding.ActivityLoginBinding
import com.hospital.app.ui.main.MainActivity
import com.hospital.app.utils.SessionManager

class LoginActivity : AppCompatActivity() {
    private lateinit var binding: ActivityLoginBinding
    private lateinit var viewModel: LoginViewModel
    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        sessionManager = SessionManager(this)
        viewModel = ViewModelProvider(this)[LoginViewModel::class.java]

        // Check if user is already logged in
        if (sessionManager.getToken() != null) {
            startMainActivity()
            finish()
            return
        }

        setupViews()
        setupObservers()
    }

    private fun setupViews() {
        binding.loginButton.setOnClickListener {
            val email = binding.emailEditText.text.toString()
            val password = binding.passwordEditText.text.toString()

            if (email.isBlank() || password.isBlank()) {
                Toast.makeText(this, "Please fill all fields", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            viewModel.login(email, password)
        }
    }

    private fun setupObservers() {
        viewModel.loginResult.observe(this) { result ->
            when (result) {
                is LoginResult.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.loginButton.isEnabled = false
                }
                is LoginResult.Success -> {
                    sessionManager.saveToken(result.token)
                    sessionManager.saveUserInfo(
                        result.userId,
                        result.name,
                        result.email,
                        result.patientNumber
                    )
                    startMainActivity()
                    finish()
                }
                is LoginResult.Error -> {
                    binding.progressBar.visibility = View.GONE
                    binding.loginButton.isEnabled = true
                    Toast.makeText(this, result.message, Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun startMainActivity() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
} 
