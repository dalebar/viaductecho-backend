package com.viaductecho.android.ui.about

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.google.android.material.snackbar.Snackbar
import com.viaductecho.android.BuildConfig
import com.viaductecho.android.R
import com.viaductecho.android.databinding.FragmentAboutBinding

class AboutFragment : Fragment() {

    private var _binding: FragmentAboutBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentAboutBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupUI()
        setupClickListeners()
    }

    private fun setupUI() {
        // Set version info
        binding.textViewVersion.text = getString(
            R.string.app_name
        ) + " v${BuildConfig.VERSION_NAME}"
    }

    private fun setupClickListeners() {
        // Email click
        binding.layoutEmail.setOnClickListener {
            openEmail()
        }

        // Phone click
        binding.layoutPhone.setOnClickListener {
            dialPhone()
        }

        // Website click
        binding.layoutWebsite.setOnClickListener {
            openWebsite(getString(R.string.contact_website))
        }

        // Privacy Policy click
        binding.layoutPrivacy.setOnClickListener {
            openWebsite("https://viaductecho.info/privacy")
        }
    }

    private fun openEmail() {
        try {
            val intent = Intent(Intent.ACTION_SENDTO).apply {
                data = Uri.parse("mailto:${getString(R.string.contact_email)}")
                putExtra(Intent.EXTRA_SUBJECT, "Viaduct Echo - Contact")
            }
            startActivity(intent)
        } catch (e: Exception) {
            showError("No email app found")
        }
    }

    private fun dialPhone() {
        try {
            val intent = Intent(Intent.ACTION_DIAL).apply {
                data = Uri.parse("tel:${getString(R.string.contact_phone)}")
            }
            startActivity(intent)
        } catch (e: Exception) {
            showError("Unable to open phone dialer")
        }
    }

    private fun openWebsite(url: String) {
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            startActivity(intent)
        } catch (e: Exception) {
            showError(getString(R.string.error_opening_link))
        }
    }

    private fun showError(message: String) {
        Snackbar.make(binding.root, message, Snackbar.LENGTH_SHORT).show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
