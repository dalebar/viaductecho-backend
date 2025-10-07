package com.viaductecho.android.ui.home

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.google.android.material.snackbar.Snackbar
import com.viaductecho.android.R
import com.viaductecho.android.databinding.FragmentHomeBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupSectionClickListeners()
    }

    private fun setupSectionClickListeners() {
        binding.apply {
            // Local News - Navigate to existing ArticleListFragment
            cardLocalNews.setOnClickListener {
                findNavController().navigate(R.id.action_homeFragment_to_articleListFragment)
            }

            // Coming Soon sections - Show snackbar
            cardEvents.setOnClickListener {
                showComingSoonMessage("Events")
            }

            cardBusinessDirectory.setOnClickListener {
                showComingSoonMessage("Places")
            }

            cardOffers.setOnClickListener {
                showComingSoonMessage("Offers")
            }

            cardContacts.setOnClickListener {
                showComingSoonMessage("Directory")
            }

            // About / Contact link
            textAboutLink.setOnClickListener {
                findNavController().navigate(R.id.action_homeFragment_to_aboutFragment)
            }
        }
    }

    private fun showComingSoonMessage(sectionName: String) {
        Snackbar.make(
            binding.root,
            "$sectionName coming soon! Stay tuned for updates.",
            Snackbar.LENGTH_SHORT
        ).show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
