package com.hospital.app.ui.cases

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.hospital.app.databinding.FragmentCasesBinding
import com.hospital.app.utils.SessionManager

class CasesFragment : Fragment() {
    private var _binding: FragmentCasesBinding? = null
    private val binding get() = _binding!!
    private lateinit var viewModel: CasesViewModel
    private lateinit var casesAdapter: CasesAdapter
    private lateinit var sessionManager: SessionManager

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentCasesBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        sessionManager = SessionManager(requireContext())
        viewModel = ViewModelProvider(this)[CasesViewModel::class.java]
        
        setupRecyclerView()
        setupObservers()
        setupSwipeRefresh()
        
        // Load cases
        viewModel.loadCases(sessionManager.getToken())
    }

    private fun setupRecyclerView() {
        casesAdapter = CasesAdapter()
        binding.recyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = casesAdapter
        }
    }

    private fun setupObservers() {
        viewModel.cases.observe(viewLifecycleOwner) { cases ->
            casesAdapter.submitList(cases)
            binding.emptyView.visibility = if (cases.isEmpty()) View.VISIBLE else View.GONE
        }

        viewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            binding.swipeRefresh.isRefreshing = isLoading
        }

        viewModel.error.observe(viewLifecycleOwner) { errorMessage ->
            // Show error message using a Snackbar or Toast
        }
    }

    private fun setupSwipeRefresh() {
        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadCases(sessionManager.getToken())
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
} 