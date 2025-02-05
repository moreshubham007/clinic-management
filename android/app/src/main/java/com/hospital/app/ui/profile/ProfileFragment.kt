package com.hospital.app.ui.profile

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.hospital.app.databinding.FragmentProfileBinding
import com.hospital.app.ui.auth.LoginActivity
import com.hospital.app.utils.SessionManager

class ProfileFragment : Fragment() {
    private var _binding: FragmentProfileBinding? = null
    private val binding get() = _binding!!
    private lateinit var viewModel: ProfileViewModel
    private lateinit var sessionManager: SessionManager

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentProfileBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        sessionManager = SessionManager(requireContext())
        viewModel = ViewModelProvider(this)[ProfileViewModel::class.java]
        
        setupViews()
        setupObservers()
        
        // Load profile
        viewModel.loadProfile(sessionManager.getToken())
    }

    private fun setupViews() {
        binding.logoutButton.setOnClickListener {
            sessionManager.clearSession()
            startActivity(Intent(requireContext(), LoginActivity::class.java))
            requireActivity().finish()
        }

        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadProfile(sessionManager.getToken())
        }
    }

    private fun setupObservers() {
        viewModel.profile.observe(viewLifecycleOwner) { user ->
            binding.apply {
                nameText.text = user.name
                emailText.text = user.email
                patientNumberText.text = user.patient_number ?: "N/A"
            }
        }

        viewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            binding.swipeRefresh.isRefreshing = isLoading
        }

        viewModel.error.observe(viewLifecycleOwner) { errorMessage ->
            // Show error message using a Snackbar or Toast
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
} 