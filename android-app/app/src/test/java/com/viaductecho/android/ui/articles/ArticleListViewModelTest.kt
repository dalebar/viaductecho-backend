package com.viaductecho.android.ui.articles

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import com.viaductecho.android.data.models.Article
import com.viaductecho.android.data.models.ArticlesResponse
import com.viaductecho.android.data.models.Pagination
import com.viaductecho.android.data.repository.ArticleRepository
import com.viaductecho.android.utils.Resource
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mock
import org.mockito.junit.MockitoJUnitRunner
import org.mockito.kotlin.whenever

@ExperimentalCoroutinesApi
@RunWith(MockitoJUnitRunner::class)
class ArticleListViewModelTest {
    
    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()
    
    @Mock
    private lateinit var repository: ArticleRepository
    
    private lateinit var viewModel: ArticleListViewModel
    private val testDispatcher = StandardTestDispatcher()
    
    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        viewModel = ArticleListViewModel(repository)
    }
    
    @Test
    fun `loadArticles sets loading state initially`() = runTest {
        // Given
        val articles = listOf(createMockArticle(1, "Test Article"))
        val pagination = Pagination(1, 20, 1, 1, false, false)
        val response = ArticlesResponse(articles, pagination)
        whenever(repository.getArticles(1, 20)).thenReturn(Resource.success(response))
        
        // When
        viewModel.loadArticles()
        
        // Then
        assertEquals(Resource.Loading<List<Article>>().javaClass, viewModel.articles.value?.javaClass)
    }
    
    @Test
    fun `loadArticles updates articles on success`() = runTest {
        // Given
        val articles = listOf(
            createMockArticle(1, "Test Article 1"),
            createMockArticle(2, "Test Article 2")
        )
        val pagination = Pagination(1, 20, 2, 1, false, false)
        val response = ArticlesResponse(articles, pagination)
        whenever(repository.getArticles(1, 20)).thenReturn(Resource.success(response))
        
        // When
        viewModel.loadArticles()
        testDispatcher.scheduler.advanceUntilIdle()
        
        // Then
        assertTrue(viewModel.articles.value is Resource.Success)
        assertEquals(2, (viewModel.articles.value as Resource.Success).data?.size)
        assertFalse(viewModel.isRefreshing.value ?: true)
    }
    
    @Test
    fun `loadArticles shows error on failure`() = runTest {
        // Given
        val errorMessage = "Network error"
        whenever(repository.getArticles(1, 20)).thenReturn(Resource.error(errorMessage))
        
        // When
        viewModel.loadArticles()
        testDispatcher.scheduler.advanceUntilIdle()
        
        // Then
        assertTrue(viewModel.articles.value is Resource.Error)
        assertEquals(errorMessage, (viewModel.articles.value as Resource.Error).message)
        assertFalse(viewModel.isRefreshing.value ?: true)
    }
    
    @Test
    fun `refreshArticles clears existing data and loads fresh`() = runTest {
        // Given - Load initial data
        val initialArticles = listOf(createMockArticle(1, "Initial Article"))
        val initialPagination = Pagination(1, 20, 1, 1, false, false)
        val initialResponse = ArticlesResponse(initialArticles, initialPagination)
        whenever(repository.getArticles(1, 20)).thenReturn(Resource.success(initialResponse))
        
        viewModel.loadArticles()
        testDispatcher.scheduler.advanceUntilIdle()
        
        // When - Refresh with new data
        val refreshedArticles = listOf(createMockArticle(2, "Refreshed Article"))
        val refreshedResponse = ArticlesResponse(refreshedArticles, initialPagination)
        whenever(repository.getArticles(1, 20)).thenReturn(Resource.success(refreshedResponse))
        
        viewModel.refreshArticles()
        testDispatcher.scheduler.advanceUntilIdle()
        
        // Then
        assertTrue(viewModel.articles.value is Resource.Success)
        assertEquals(1, (viewModel.articles.value as Resource.Success).data?.size)
        assertEquals("Refreshed Article", (viewModel.articles.value as Resource.Success).data?.first()?.title)
        assertFalse(viewModel.isRefreshing.value ?: true)
    }
    
    @Test
    fun `loadMoreArticles appends to existing data`() = runTest {
        // Given - Load initial page
        val page1Articles = listOf(createMockArticle(1, "Article 1"))
        val page1Pagination = Pagination(1, 20, 2, 2, true, false)
        val page1Response = ArticlesResponse(page1Articles, page1Pagination)
        whenever(repository.getArticles(1, 20)).thenReturn(Resource.success(page1Response))
        
        viewModel.loadArticles()
        testDispatcher.scheduler.advanceUntilIdle()
        
        // When - Load more
        val page2Articles = listOf(createMockArticle(2, "Article 2"))
        val page2Pagination = Pagination(2, 20, 2, 2, false, true)
        val page2Response = ArticlesResponse(page2Articles, page2Pagination)
        whenever(repository.getArticles(2, 20)).thenReturn(Resource.success(page2Response))
        
        viewModel.loadMoreArticles()
        testDispatcher.scheduler.advanceUntilIdle()
        
        // Then
        assertTrue(viewModel.articles.value is Resource.Success)
        assertEquals(2, (viewModel.articles.value as Resource.Success).data?.size)
        assertTrue(viewModel.isLastPage.value ?: false)
        assertFalse(viewModel.isLoadingMore.value ?: true)
    }
    
    @Test
    fun `loadMoreArticles does not load when already loading`() = runTest {
        // Given - Set loading state
        viewModel.loadArticles()
        
        // When - Try to load more while already loading
        val initialLoadingState = viewModel.isLoadingMore.value
        viewModel.loadMoreArticles()
        
        // Then - Should not change loading state
        assertEquals(initialLoadingState, viewModel.isLoadingMore.value)
    }
    
    @Test
    fun `loadMoreArticles does not load when is last page`() = runTest {
        // Given - Load data that is last page
        val articles = listOf(createMockArticle(1, "Last Article"))
        val pagination = Pagination(1, 20, 1, 1, false, false)
        val response = ArticlesResponse(articles, pagination)
        whenever(repository.getArticles(1, 20)).thenReturn(Resource.success(response))
        
        viewModel.loadArticles()
        testDispatcher.scheduler.advanceUntilIdle()
        
        // When - Try to load more when on last page
        viewModel.loadMoreArticles()
        
        // Then - Should not start loading
        assertFalse(viewModel.isLoadingMore.value ?: false)
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