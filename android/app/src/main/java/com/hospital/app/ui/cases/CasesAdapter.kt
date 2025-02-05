package com.hospital.app.ui.cases

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.hospital.app.R
import com.hospital.app.api.Case
import com.hospital.app.databinding.ItemCaseBinding
import java.text.SimpleDateFormat
import java.util.*

class CasesAdapter : ListAdapter<Case, CasesAdapter.CaseViewHolder>(CaseDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CaseViewHolder {
        val binding = ItemCaseBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return CaseViewHolder(binding)
    }

    override fun onBindViewHolder(holder: CaseViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class CaseViewHolder(
        private val binding: ItemCaseBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())

        fun bind(case: Case) {
            binding.apply {
                doctorName.text = case.doctor.name
                caseDate.text = formatDate(case.created_at)
                caseStatus.text = case.status.replaceFirstChar { it.uppercase() }
                caseStatus.setChipBackgroundColorResource(getStatusColor(case.status))
                caseDiagnosis.text = case.diagnosis ?: "No diagnosis yet"
                caseTreatment.text = case.treatment ?: "No treatment plan yet"
            }
        }

        private fun formatDate(dateStr: String): String {
            return try {
                val date = dateFormat.parse(dateStr)
                dateFormat.format(date!!)
            } catch (e: Exception) {
                dateStr
            }
        }

        private fun getStatusColor(status: String): Int {
            return when (status.lowercase()) {
                "open" -> R.color.status_scheduled
                "closed" -> R.color.status_completed
                "pending" -> R.color.status_default
                else -> R.color.status_default
            }
        }
    }

    private class CaseDiffCallback : DiffUtil.ItemCallback<Case>() {
        override fun areItemsTheSame(oldItem: Case, newItem: Case): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Case, newItem: Case): Boolean {
            return oldItem == newItem
        }
    }
} 