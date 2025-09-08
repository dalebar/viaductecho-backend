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
class ArticleDetailViewModel @Inject constructor(
    private val repository: ArticleRepository
) : ViewModel() {
    
    private val _article = MutableLiveData<Resource<Article>>()
    val article: LiveData<Resource<Article>> = _article
    
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading
    
    fun loadArticle(articleId: Int) {
        _article.value = Resource.loading()
        _isLoading.value = true
        
        viewModelScope.launch {
            try {
                val result = repository.getArticleById(articleId)
                _article.value = result
            } catch (e: Exception) {
                _article.value = Resource.error(e.message ?: "Unknown error occurred")
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun retry(articleId: Int) {
        loadArticle(articleId)
    }
}