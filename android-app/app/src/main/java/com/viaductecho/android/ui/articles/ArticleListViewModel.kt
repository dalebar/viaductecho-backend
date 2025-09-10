package com.viaductecho.android.ui.articles

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.viaductecho.android.data.models.Article
import com.viaductecho.android.data.repository.ArticleRepository
import com.viaductecho.android.utils.Resource
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ArticleListViewModel @Inject constructor(
    private val repository: ArticleRepository
) : ViewModel() {

    private val _articles = MutableLiveData<Resource<List<Article>>>()
    val articles: LiveData<Resource<List<Article>>> = _articles

    private val _isRefreshing = MutableLiveData<Boolean>()
    val isRefreshing: LiveData<Boolean> = _isRefreshing

    private val _isLoadingMore = MutableLiveData<Boolean>()
    val isLoadingMore: LiveData<Boolean> = _isLoadingMore

    private val _isLastPage = MutableLiveData<Boolean>()
    val isLastPage: LiveData<Boolean> = _isLastPage

    private var currentPage = 1
    private var totalPages = 1
    private val articlesPerPage = 20
    private val allArticles = mutableListOf<Article>()

    fun loadArticles(refresh: Boolean = false) {
        if (refresh) {
            currentPage = 1
            allArticles.clear()
            _isRefreshing.value = true
        } else if (allArticles.isEmpty()) {
            _articles.value = Resource.loading()
        }

        viewModelScope.launch {
            try {
                val result = repository.getArticles(
                    page = currentPage,
                    perPage = articlesPerPage
                )

                when (result) {
                    is Resource.Success -> {
                        result.data?.let { response ->
                            if (refresh) {
                                allArticles.clear()
                            }

                            allArticles.addAll(response.articles)
                            totalPages = response.pagination.totalPages

                            _articles.value = Resource.success(allArticles.toList())
                            _isLastPage.value = currentPage >= totalPages

                            if (!_isLastPage.value!!) {
                                currentPage++
                            }
                        } ?: run {
                            _articles.value = Resource.error("No data received")
                        }
                    }

                    is Resource.Error -> {
                        if (allArticles.isEmpty()) {
                            _articles.value = Resource.error(result.message ?: "Unknown error")
                        } else {
                            // Show error but keep existing data
                            _articles.value = Resource.success(allArticles.toList())
                        }
                    }

                    is Resource.Loading -> {
                        // Handle loading state if needed
                    }
                }
            } catch (e: Exception) {
                _articles.value = Resource.error(e.message ?: "Unknown error")
            } finally {
                _isRefreshing.value = false
                _isLoadingMore.value = false
            }
        }
    }

    fun refreshArticles() {
        loadArticles(refresh = true)
    }

    fun loadMoreArticles() {
        if (_isLoadingMore.value == true || _isLastPage.value == true) {
            return
        }

        _isLoadingMore.value = true
        loadArticles(refresh = false)
    }

    fun retry() {
        if (allArticles.isEmpty()) {
            loadArticles()
        } else {
            loadMoreArticles()
        }
    }
}
