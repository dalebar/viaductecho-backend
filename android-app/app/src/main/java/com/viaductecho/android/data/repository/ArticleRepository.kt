package com.viaductecho.android.data.repository

import android.util.Log
import com.viaductecho.android.data.api.ApiService
import com.viaductecho.android.data.models.Article
import com.viaductecho.android.data.models.ArticlesResponse
import com.viaductecho.android.data.models.HealthResponse
import com.viaductecho.android.data.models.SourcesResponse
import com.viaductecho.android.utils.Resource
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import retrofit2.Response
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ArticleRepository @Inject constructor(
    private val apiService: ApiService
) {
    companion object {
        private const val TAG = "ArticleRepository"
    }

    suspend fun getHealth(): Resource<HealthResponse> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getHealth()
            handleResponse(response, "Failed to check API health")
        } catch (e: Exception) {
            Log.e(TAG, "Health check failed", e)
            Resource.error("Network error: ${e.message}")
        }
    }

    suspend fun getArticles(
        page: Int = 1,
        perPage: Int = 20,
        source: String? = null,
        processedOnly: Boolean = true
    ): Resource<ArticlesResponse> = withContext(Dispatchers.IO) {
        try {
            Log.d(TAG, "Fetching articles - page: $page, source: $source")
            val response = apiService.getArticles(page, perPage, source, processedOnly)
            handleResponse(response, "Failed to fetch articles")
        } catch (e: IOException) {
            Log.e(TAG, "Network error fetching articles", e)
            Resource.error("No internet connection")
        } catch (e: Exception) {
            Log.e(TAG, "Unknown error fetching articles", e)
            Resource.error("Something went wrong: ${e.message}")
        }
    }

    suspend fun getArticleById(articleId: Int): Resource<Article> = withContext(Dispatchers.IO) {
        try {
            Log.d(TAG, "Fetching article by ID: $articleId")
            val response = apiService.getArticleById(articleId)
            handleResponse(response, "Failed to fetch article details")
        } catch (e: IOException) {
            Log.e(TAG, "Network error fetching article $articleId", e)
            Resource.error("No internet connection")
        } catch (e: Exception) {
            Log.e(TAG, "Unknown error fetching article $articleId", e)
            Resource.error("Something went wrong: ${e.message}")
        }
    }

    suspend fun getRecentArticles(
        hours: Int = 24,
        limit: Int = 10
    ): Resource<ArticlesResponse> = withContext(Dispatchers.IO) {
        try {
            Log.d(TAG, "Fetching recent articles - hours: $hours, limit: $limit")
            val response = apiService.getRecentArticles(hours, limit)
            handleResponse(response, "Failed to fetch recent articles")
        } catch (e: Exception) {
            Log.e(TAG, "Error fetching recent articles", e)
            Resource.error("Network error: ${e.message}")
        }
    }

    suspend fun searchArticles(
        query: String,
        page: Int = 1,
        perPage: Int = 20
    ): Resource<ArticlesResponse> = withContext(Dispatchers.IO) {
        try {
            Log.d(TAG, "Searching articles - query: '$query', page: $page")
            val response = apiService.searchArticles(query, page, perPage)
            handleResponse(response, "Failed to search articles")
        } catch (e: Exception) {
            Log.e(TAG, "Error searching articles", e)
            Resource.error("Network error: ${e.message}")
        }
    }

    suspend fun getSources(): Resource<SourcesResponse> = withContext(Dispatchers.IO) {
        try {
            Log.d(TAG, "Fetching sources")
            val response = apiService.getSources()
            handleResponse(response, "Failed to fetch sources")
        } catch (e: Exception) {
            Log.e(TAG, "Error fetching sources", e)
            Resource.error("Network error: ${e.message}")
        }
    }

    private fun <T> handleResponse(response: Response<T>, errorMessage: String): Resource<T> {
        return if (response.isSuccessful) {
            response.body()?.let { body ->
                Log.d(TAG, "API call successful")
                Resource.success(body)
            } ?: run {
                Log.w(TAG, "API response body is null")
                Resource.error("$errorMessage: Empty response")
            }
        } else {
            val error = "$errorMessage: ${response.code()} ${response.message()}"
            Log.e(TAG, error)
            Resource.error(error)
        }
    }
}