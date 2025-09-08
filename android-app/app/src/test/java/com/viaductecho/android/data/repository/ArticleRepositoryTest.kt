package com.viaductecho.android.data.repository

import com.viaductecho.android.data.api.ApiService
import com.viaductecho.android.data.models.Article
import com.viaductecho.android.data.models.ArticlesResponse
import com.viaductecho.android.data.models.HealthResponse
import com.viaductecho.android.data.models.Pagination
import com.viaductecho.android.utils.Resource
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mock
import org.mockito.junit.MockitoJUnitRunner
import org.mockito.kotlin.whenever
import retrofit2.Response
import java.io.IOException

@RunWith(MockitoJUnitRunner::class)
class ArticleRepositoryTest {
    
    @Mock
    private lateinit var apiService: ApiService
    
    private lateinit var repository: ArticleRepository
    
    @Before
    fun setup() {
        repository = ArticleRepository(apiService)
    }
    
    @Test
    fun `getHealth returns success when API call succeeds`() = runTest {
        // Given
        val healthResponse = HealthResponse(
            status = "healthy",
            totalArticles = 100,
            recentArticles24h = 10,
            databaseConnected = true,
            timestamp = "2024-03-15T10:00:00Z"
        )
        whenever(apiService.getHealth()).thenReturn(Response.success(healthResponse))
        
        // When
        val result = repository.getHealth()
        
        // Then
        assertTrue(result is Resource.Success)
        assertEquals(healthResponse, (result as Resource.Success).data)
    }
    
    @Test
    fun `getHealth returns error when API call fails`() = runTest {
        // Given
        whenever(apiService.getHealth()).thenThrow(IOException("Network error"))
        
        // When
        val result = repository.getHealth()
        
        // Then
        assertTrue(result is Resource.Error)
        assertTrue((result as Resource.Error).message!!.contains("Network error"))
    }
    
    @Test
    fun `getArticles returns success with articles when API call succeeds`() = runTest {
        // Given
        val articles = listOf(
            createMockArticle(1, "Test Article 1"),
            createMockArticle(2, "Test Article 2")
        )
        val pagination = Pagination(1, 20, 2, 1, false, false)
        val articlesResponse = ArticlesResponse(articles, pagination)
        
        whenever(apiService.getArticles(1, 20, null, true))
            .thenReturn(Response.success(articlesResponse))
        
        // When
        val result = repository.getArticles()
        
        // Then
        assertTrue(result is Resource.Success)
        assertEquals(articlesResponse, (result as Resource.Success).data)
        assertEquals(2, result.data.articles.size)
    }
    
    @Test
    fun `getArticles returns error when network is unavailable`() = runTest {
        // Given
        whenever(apiService.getArticles(1, 20, null, true))
            .thenThrow(IOException("No internet connection"))
        
        // When
        val result = repository.getArticles()
        
        // Then
        assertTrue(result is Resource.Error)
        assertEquals("No internet connection", (result as Resource.Error).message)
    }
    
    @Test
    fun `getArticleById returns success when article exists`() = runTest {
        // Given
        val article = createMockArticle(1, "Test Article")
        whenever(apiService.getArticleById(1)).thenReturn(Response.success(article))
        
        // When
        val result = repository.getArticleById(1)
        
        // Then
        assertTrue(result is Resource.Success)
        assertEquals(article, (result as Resource.Success).data)
    }
    
    @Test
    fun `getArticleById returns error when article not found`() = runTest {
        // Given
        whenever(apiService.getArticleById(999))
            .thenReturn(Response.error(404, okhttp3.ResponseBody.create(null, "")))
        
        // When
        val result = repository.getArticleById(999)
        
        // Then
        assertTrue(result is Resource.Error)
        assertTrue((result as Resource.Error).message!!.contains("404"))
    }
    
    private fun createMockArticle(id: Int, title: String) = Article(
        id = id,
        title = title,
        link = "https://example.com/article/$id",
        summary = "Summary for $title",
        source = "Test Source",
        sourceType = "RSS",
        publishedDate = "2024-03-15T10:00:00+00:00",
        createdAt = "2024-03-15T10:00:00+00:00",
        imageUrl = "https://example.com/image/$id.jpg",
        aiSummary = "AI summary for $title",
        extractedContent = "Full content for $title",
        processed = true,
        updatedAt = "2024-03-15T10:00:00+00:00"
    )
}