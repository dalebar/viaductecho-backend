package com.viaductecho.android.ui.articles

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.snackbar.Snackbar
import com.viaductecho.android.R
import com.viaductecho.android.data.models.Article
import com.viaductecho.android.databinding.FragmentArticleListBinding
import com.viaductecho.android.utils.Resource
import com.viaductecho.android.utils.isNetworkAvailable
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class ArticleListFragment : Fragment() {

    private var _binding: FragmentArticleListBinding? = null
    private val binding get() = _binding!!

    private val viewModel: ArticleListViewModel by viewModels()
    private lateinit var articleAdapter: ArticleListAdapter


    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentArticleListBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        setupSwipeRefresh()
        setupObservers()

        // Load articles if not already loaded
        val currentData = viewModel.articles.value
        if (currentData == null || (currentData is Resource.Success && currentData.data.isEmpty()) || currentData is Resource.Error) {
            viewModel.loadArticles()
        }
    }

    private fun setupRecyclerView() {
        articleAdapter = ArticleListAdapter { article ->
            navigateToArticleDetail(article)
        }

        binding.recyclerViewArticles.apply {
            adapter = articleAdapter
            layoutManager = LinearLayoutManager(requireContext())

            // Add pagination scroll listener
            addOnScrollListener(object : RecyclerView.OnScrollListener() {
                override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
                    super.onScrolled(recyclerView, dx, dy)

                    val layoutManager = recyclerView.layoutManager as LinearLayoutManager
                    val visibleItemCount = layoutManager.childCount
                    val totalItemCount = layoutManager.itemCount
                    val firstVisibleItemPosition = layoutManager.findFirstVisibleItemPosition()

                    val isLoading = viewModel.isLoadingMore.value ?: false
                    val isLastPage = viewModel.isLastPage.value ?: false

                    if (!isLoading && !isLastPage) {
                        if (visibleItemCount + firstVisibleItemPosition >= totalItemCount
                            && firstVisibleItemPosition >= 0
                            && totalItemCount >= 20) {
                            loadMoreArticles()
                        }
                    }
                }
            })
        }
    }

    private fun setupSwipeRefresh() {
        binding.swipeRefreshLayout.apply {
            setColorSchemeResources(
                R.color.md_theme_light_primary,
                R.color.md_theme_light_secondary,
                R.color.md_theme_light_tertiary
            )

            setOnRefreshListener {
                if (requireContext().isNetworkAvailable()) {
                    viewModel.refreshArticles()
                } else {
                    isRefreshing = false
                    showNetworkError()
                }
            }
        }
    }

    private fun setupObservers() {
        viewModel.articles.observe(viewLifecycleOwner) { resource ->
            when (resource) {
                is Resource.Loading -> {
                    showLoading()
                }
                is Resource.Success -> {
                    hideLoading()
                    val articles = resource.data
                    if (articles.isEmpty()) {
                        showEmptyState()
                    } else {
                        hideEmptyState()
                        articleAdapter.submitList(articles)
                    }
                }
                is Resource.Error -> {
                    hideLoading()
                    showError(resource.message ?: getString(R.string.error_unknown))
                }
            }
        }

        viewModel.isRefreshing.observe(viewLifecycleOwner) { isRefreshing ->
            binding.swipeRefreshLayout.isRefreshing = isRefreshing
        }

        viewModel.isLoadingMore.observe(viewLifecycleOwner) { isLoadingMore ->
            // Show/hide loading more indicator if needed
        }

        viewModel.isLastPage.observe(viewLifecycleOwner) { lastPage ->
            // Update pagination state
        }
    }

    private fun loadMoreArticles() {
        if (requireContext().isNetworkAvailable()) {
            viewModel.loadMoreArticles()
        }
    }

    private fun navigateToArticleDetail(article: Article) {
        val action = ArticleListFragmentDirections
            .actionArticleListFragmentToArticleDetailFragment(
                articleId = article.id,
                article = article
            )
        findNavController().navigate(action)
    }

    private fun showLoading() {
        if (articleAdapter.itemCount == 0) {
            binding.progressBar.visibility = View.VISIBLE
            binding.recyclerViewArticles.visibility = View.GONE
            binding.emptyStateView.visibility = View.GONE
        }
    }

    private fun hideLoading() {
        binding.progressBar.visibility = View.GONE
        binding.recyclerViewArticles.visibility = View.VISIBLE
        binding.swipeRefreshLayout.isRefreshing = false
    }

    private fun showEmptyState() {
        binding.emptyStateView.visibility = View.VISIBLE
        binding.recyclerViewArticles.visibility = View.GONE
    }

    private fun hideEmptyState() {
        binding.emptyStateView.visibility = View.GONE
        binding.recyclerViewArticles.visibility = View.VISIBLE
    }

    private fun showError(message: String) {
        Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG)
            .setAction(getString(R.string.retry)) {
                viewModel.loadArticles()
            }
            .show()
    }

    private fun showNetworkError() {
        Snackbar.make(binding.root, getString(R.string.error_network), Snackbar.LENGTH_LONG)
            .show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Clear SwipeRefreshLayout listener to prevent fragment capture leak
        binding.swipeRefreshLayout.setOnRefreshListener(null)
        // Clear scroll listeners to prevent fragment capture leak
        binding.recyclerViewArticles.clearOnScrollListeners()
        // Clear lambda callbacks to prevent fragment capture leak
        articleAdapter.clearCallbacks()
        // Clear any pending Glide requests for the RecyclerView
        binding.recyclerViewArticles.adapter = null
        _binding = null
    }
}
