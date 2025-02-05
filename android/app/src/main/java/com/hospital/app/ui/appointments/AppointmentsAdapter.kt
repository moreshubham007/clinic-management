package com.hospital.app.ui.appointments

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.hospital.app.R
import com.hospital.app.api.Appointment
import com.hospital.app.databinding.ItemAppointmentBinding
import java.text.SimpleDateFormat
import java.util.*

class AppointmentsAdapter(
    private val onAppointmentClick: (Appointment) -> Unit
) : ListAdapter<Appointment, AppointmentsAdapter.AppointmentViewHolder>(AppointmentDiffCallback()) {

    // Create date formatters as static objects to avoid creating new instances for each item
    companion object {
        private val INPUT_DATE_FORMAT = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
        private val DISPLAY_DATE_FORMAT = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault())
        private val DISPLAY_TIME_FORMAT = SimpleDateFormat("hh:mm a", Locale.getDefault())
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): AppointmentViewHolder {
        val binding = ItemAppointmentBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return AppointmentViewHolder(binding, onAppointmentClick)
    }

    override fun onBindViewHolder(holder: AppointmentViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class AppointmentViewHolder(
        private val binding: ItemAppointmentBinding,
        private val onAppointmentClick: (Appointment) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(appointment: Appointment) {
            binding.apply {
                root.setOnClickListener { onAppointmentClick(appointment) }
                
                doctorName.text = appointment.doctor.name
                doctorSpecialization.text = appointment.doctor.specialization
                
                // Format date and time
                try {
                    val date = INPUT_DATE_FORMAT.parse(appointment.datetime)
                    if (date != null) {
                        appointmentDate.text = buildString {
                            append(DISPLAY_DATE_FORMAT.format(date))
                            append(" at ")
                            append(DISPLAY_TIME_FORMAT.format(date))
                        }
                    } else {
                        appointmentDate.text = appointment.datetime
                    }
                } catch (e: Exception) {
                    appointmentDate.text = appointment.datetime
                }

                // Set appointment status with appropriate color
                appointmentStatus.apply {
                    text = appointment.status.replaceFirstChar { it.uppercase() }
                    setChipBackgroundColorResource(getStatusColor(appointment.status))
                }

                // Show notes if available
                if (!appointment.notes.isNullOrBlank()) {
                    appointmentNotes.apply {
                        visibility = View.VISIBLE
                        text = appointment.notes
                    }
                } else {
                    appointmentNotes.visibility = View.GONE
                }

                // Set status-based icon tint
                doctorIcon.setColorFilter(
                    ContextCompat.getColor(
                        root.context,
                        getStatusColor(appointment.status)
                    )
                )
            }
        }

        private fun getStatusColor(status: String): Int {
            return when (status.lowercase()) {
                "scheduled" -> R.color.status_scheduled
                "completed" -> R.color.status_completed
                "cancelled" -> R.color.status_cancelled
                else -> R.color.status_default
            }
        }
    }

    private class AppointmentDiffCallback : DiffUtil.ItemCallback<Appointment>() {
        override fun areItemsTheSame(oldItem: Appointment, newItem: Appointment): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Appointment, newItem: Appointment): Boolean {
            return oldItem == newItem
        }
    }
} 