package com.hospital.app.ui.appointments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.DefaultItemAnimator
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.chip.Chip
import com.google.android.material.snackbar.Snackbar
import com.hospital.app.R
import com.hospital.app.api.Appointment
import com.hospital.app.databinding.FragmentAppointmentsBinding
import com.hospital.app.utils.SessionManager

class AppointmentsFragment : Fragment() {
    private var _binding: FragmentAppointmentsBinding? = null
    private val binding get() = _binding!!
    private lateinit var viewModel: AppointmentsViewModel
    private lateinit var appointmentsAdapter: AppointmentsAdapter
    private lateinit var sessionManager: SessionManager
    private var currentFilter: String? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentAppointmentsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        sessionManager = SessionManager(requireContext())
        viewModel = ViewModelProvider(this)[AppointmentsViewModel::class.java]
        
        setupRecyclerView()
        setupObservers()
        setupSwipeRefresh()
        setupFilterChips()
        setupFab()
        
        // Load appointments
        loadAppointments()
    }

    private fun setupRecyclerView() {
        appointmentsAdapter = AppointmentsAdapter(::onAppointmentClick)
        binding.recyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = appointmentsAdapter
            setHasFixedSize(true)
            itemAnimator = DefaultItemAnimator().apply {
                supportsChangeAnimations = false
            }
        }
    }

    private fun onAppointmentClick(appointment: Appointment) {
        // TODO: Navigate to appointment details
        val message = when (appointment.status.toLowerCase()) {
            "scheduled" -> "View or reschedule appointment"
            "completed" -> "View appointment details and doctor's notes"
            "cancelled" -> "View cancellation details"
            else -> "View appointment details"
        }
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }

    private fun setupFilterChips() {
        // Use string resources for chip text
        binding.chipAll.text = getString(R.string.filter_all)
        binding.chipScheduled.text = getString(R.string.filter_scheduled)
        binding.chipCompleted.text = getString(R.string.filter_completed)
        binding.chipCancelled.text = getString(R.string.filter_cancelled)

        binding.filterChipGroup.setOnCheckedStateChangeListener { group, checkedIds ->
            if (checkedIds.isEmpty()) {
                // If no chip is selected, select the "All" chip
                binding.chipAll.isChecked = true
                return@setOnCheckedStateChangeListener
            }

            val chip = group.findViewById<Chip>(checkedIds[0])
            currentFilter = when (chip.id) {
                R.id.chipAll -> null
                R.id.chipScheduled -> "scheduled"
                R.id.chipCompleted -> "completed"
                R.id.chipCancelled -> "cancelled"
                else -> null
            }?.lowercase()
            loadAppointments()
        }
    }

    private fun setupFab() {
        binding.fabNewAppointment.apply {
            text = getString(R.string.book_appointment)
            setOnClickListener {
                // TODO: Navigate to new appointment screen
                Toast.makeText(context, "Book new appointment coming soon!", Toast.LENGTH_SHORT).show()
            }
        }

        // Hide/show FAB on scroll with animation
        binding.recyclerView.addOnScrollListener(object : androidx.recyclerview.widget.RecyclerView.OnScrollListener() {
            override fun onScrolled(recyclerView: androidx.recyclerview.widget.RecyclerView, dx: Int, dy: Int) {
                if (dy > 0 && binding.fabNewAppointment.isVisible) {
                    binding.fabNewAppointment.hide()
                } else if (dy < 0 && !binding.fabNewAppointment.isVisible) {
                    binding.fabNewAppointment.show()
                }
            }
        })
    }

    private fun setupObservers() {
        viewModel.appointments.observe(viewLifecycleOwner) { appointments ->
            binding.progressBar.visibility = View.GONE
            appointmentsAdapter.submitList(appointments)
            
            if (appointments.isEmpty()) {
                showEmptyState(currentFilter)
                binding.recyclerView.visibility = View.GONE
            } else {
                binding.emptyView.visibility = View.GONE
                binding.recyclerView.visibility = View.VISIBLE
            }
        }

        viewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            binding.swipeRefresh.isRefreshing = isLoading
            binding.progressBar.visibility = if (isLoading && appointmentsAdapter.currentList.isEmpty()) 
                View.VISIBLE else View.GONE
        }

        viewModel.error.observe(viewLifecycleOwner) { errorMessage ->
            binding.progressBar.visibility = View.GONE
            if (errorMessage != null) {
                val message = when {
                    errorMessage.contains("No internet") -> getString(R.string.error_network)
                    errorMessage.contains("Session expired") -> getString(R.string.error_session_expired)
                    errorMessage.contains("permission") -> getString(R.string.error_permission)
                    else -> errorMessage
                }
                
                Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG)
                    .setAction(getString(R.string.retry)) { loadAppointments() }
                    .show()
            }
        }
    }

    private fun showEmptyState(filter: String?) {
        binding.emptyView.visibility = View.VISIBLE
        binding.emptyTitleText.text = when (filter) {
            "scheduled" -> getString(R.string.no_scheduled_appointments)
            "completed" -> getString(R.string.no_completed_appointments)
            "cancelled" -> getString(R.string.no_cancelled_appointments)
            else -> getString(R.string.no_appointments_found)
        }
    }

    private fun setupSwipeRefresh() {
        binding.swipeRefresh.setOnRefreshListener {
            loadAppointments()
        }
    }

    private fun loadAppointments() {
        val token = sessionManager.getToken()
        if (token == null) {
            Snackbar.make(binding.root, getString(R.string.error_session_expired), Snackbar.LENGTH_LONG).show()
            return
        }
        viewModel.loadAppointments(token, currentFilter)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
} 