package com.viaductecho.android.ui.articles

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.Menu
import android.view.MenuInflater
import android.view.MenuItem
import android.view.View
import android.view.ViewGroup
import androidx.core.view.MenuProvider
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.Lifecycle
import androidx.navigation.fragment.navArgs
import com.google.android.material.snackbar.Snackbar
import com.viaductecho.android.R
import com.viaductecho.android.data.models.Article
import com.viaductecho.android.databinding.FragmentArticleDetailBinding
import com.viaductecho.android.utils.DateUtils
import com.viaductecho.android.utils.Resource
import com.viaductecho.android.utils.loadImage
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class ArticleDetailFragment : Fragment(), MenuProvider {
    
    private var _binding: FragmentArticleDetailBinding? = null
    private val binding get() = _binding!!
    
    private val args: ArticleDetailFragmentArgs by navArgs()
    private val viewModel: ArticleDetailViewModel by viewModels()
    
    private var currentArticle: Article? = null
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentArticleDetailBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        requireActivity().addMenuProvider(this, viewLifecycleOwner, Lifecycle.State.RESUMED)

        setupUI()
        setupObservers()

        // Always fetch full article details to get AI summary and extracted content
        // The article from the list doesn't include AI summaries
        val articleId = args.article?.id ?: args.articleId
        if (articleId > 0) {
            viewModel.loadArticle(articleId)
        } else {
            showError("Invalid article ID")
        }
    }

    private fun setupUI() {
        binding.apply {
            // Setup scroll behavior
            nestedScrollView.setOnScrollChangeListener { _, _, scrollY, _, _ ->
                // Handle scroll events if needed (e.g., hiding/showing FAB)
            }
            
            // Setup read full article button
            buttonReadFullArticle.setOnClickListener {
                currentArticle?.let { article ->
                    openExternalLink(article.link)
                }
            }
        }
    }
    
    private fun setupObservers() {
        viewModel.article.observe(viewLifecycleOwner) { resource ->
            when (resource) {
                is Resource.Loading -> {
                    showLoading()
                }
                is Resource.Success -> {
                    hideLoading()
                    resource.data?.let { article ->
                        currentArticle = article
                        displayArticle(article)
                    }
                }
                is Resource.Error -> {
                    hideLoading()
                    showError(resource.message ?: getString(R.string.error_unknown))
                }
            }
        }
    }
    
    private fun displayArticle(article: Article) {
        binding.apply {
            // Load article image
            imageViewArticle.loadImage(
                url = article.imageUrl,
                placeholder = R.drawable.placeholder_article,
                error = R.drawable.error_image
            )
            
            // Set article title
            textViewTitle.text = article.title
            
            // Set source and date information
            textViewSource.text = getString(R.string.article_source, article.source)
            textViewDate.text = article.publishedDate?.let { 
                getString(R.string.published_on, DateUtils.formatDisplayDate(it))
            } ?: ""
            
            // Display AI Summary if available
            if (!article.aiSummary.isNullOrBlank()) {
                aiSummaryContainer.visibility = View.VISIBLE
                textViewAiSummary.text = article.aiSummary
                textViewAiSummary.alpha = 1.0f // Reset opacity for real content
            } else {
                // Show a placeholder message for missing AI summaries
                aiSummaryContainer.visibility = View.VISIBLE
                textViewAiSummary.text = getString(R.string.ai_summary_not_available)
                textViewAiSummary.alpha = 0.7f // Make it slightly faded to indicate it's placeholder text
            }
            
            // Hide the original content - only show AI summary
            textViewContent.visibility = View.GONE
            
            // Setup accessibility
            imageViewArticle.contentDescription = 
                getString(R.string.cd_article_image)
            buttonReadFullArticle.contentDescription = 
                getString(R.string.cd_external_link)
        }
    }
    
    private fun showLoading() {
        binding.apply {
            progressBar.visibility = View.VISIBLE
            contentContainer.visibility = View.GONE
        }
    }
    
    private fun hideLoading() {
        binding.apply {
            progressBar.visibility = View.GONE
            contentContainer.visibility = View.VISIBLE
        }
    }
    
    private fun showError(message: String) {
        Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG)
            .setAction(getString(R.string.retry)) {
                viewModel.loadArticle(args.articleId)
            }
            .show()
    }
    
    private fun openExternalLink(url: String) {
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            startActivity(intent)
        } catch (e: Exception) {
            Snackbar.make(
                binding.root,
                getString(R.string.error_opening_link),
                Snackbar.LENGTH_SHORT
            ).show()
        }
    }
    
    private fun shareArticle() {
        currentArticle?.let { article ->
            val shareText = "${article.title}\n\n${article.link}"
            val shareIntent = Intent().apply {
                action = Intent.ACTION_SEND
                type = "text/plain"
                putExtra(Intent.EXTRA_TEXT, shareText)
                putExtra(Intent.EXTRA_SUBJECT, article.title)
            }
            
            startActivity(Intent.createChooser(shareIntent, getString(R.string.share_article)))
        }
    }
    
    // MenuProvider implementation
    override fun onCreateMenu(menu: Menu, menuInflater: MenuInflater) {
        menuInflater.inflate(R.menu.article_detail_menu, menu)
    }
    
    override fun onMenuItemSelected(menuItem: MenuItem): Boolean {
        return when (menuItem.itemId) {
            R.id.action_share -> {
                shareArticle()
                true
            }
            else -> false
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}