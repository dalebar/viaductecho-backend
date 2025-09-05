package com.viaductecho.android.utils

import android.os.Handler
import android.os.Looper
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.LifecycleOwner
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * Performance optimization utilities for the app
 */
object PerformanceUtils {
    
    /**
     * Debounce function calls to prevent excessive API calls
     */
    class Debouncer(private val delayMs: Long = 300L) {
        private var job: Job? = null
        private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
        
        fun submit(action: () -> Unit) {
            job?.cancel()
            job = scope.launch {
                delay(delayMs)
                action()
            }
        }
        
        fun cancel() {
            job?.cancel()
        }
    }
    
    /**
     * Throttle function calls to limit frequency
     */
    class Throttler(private val intervalMs: Long = 1000L) {
        private var lastActionTime = 0L
        
        fun submit(action: () -> Unit): Boolean {
            val currentTime = System.currentTimeMillis()
            if (currentTime - lastActionTime >= intervalMs) {
                lastActionTime = currentTime
                action()
                return true
            }
            return false
        }
    }
    
    /**
     * Lifecycle-aware task executor that automatically cancels when destroyed
     */
    class LifecycleTaskExecutor(private val lifecycleOwner: LifecycleOwner) {
        private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
        private val jobs = mutableListOf<Job>()
        
        init {
            lifecycleOwner.lifecycle.addObserver(LifecycleEventObserver { _, event ->
                if (event == Lifecycle.Event.ON_DESTROY) {
                    cancelAll()
                }
            })
        }
        
        fun execute(task: suspend () -> Unit): Job {
            val job = scope.launch {
                task()
            }
            jobs.add(job)
            
            job.invokeOnCompletion {
                jobs.remove(job)
            }
            
            return job
        }
        
        fun cancelAll() {
            jobs.forEach { it.cancel() }
            jobs.clear()
        }
    }
    
    /**
     * Memory-efficient image preloader
     */
    class ImagePreloader(private val context: android.content.Context) {
        private val handler = Handler(Looper.getMainLooper())
        private val preloadQueue = mutableListOf<String>()
        
        fun preloadImages(urls: List<String>, delayBetweenLoads: Long = 100L) {
            preloadQueue.clear()
            preloadQueue.addAll(urls.filterNotNull())
            
            preloadNextImage(delayBetweenLoads)
        }
        
        private fun preloadNextImage(delay: Long) {
            if (preloadQueue.isNotEmpty()) {
                val url = preloadQueue.removeFirst()
                ImageLoadingUtils.preloadImage(context, url)
                
                handler.postDelayed({
                    preloadNextImage(delay)
                }, delay)
            }
        }
        
        fun clear() {
            preloadQueue.clear()
            handler.removeCallbacksAndMessages(null)
        }
    }
    
    /**
     * Lazy initialization helper for expensive operations
     */
    class LazyInitializer<T>(private val initializer: () -> T) {
        private var value: T? = null
        private var isInitialized = false
        
        fun get(): T {
            if (!isInitialized) {
                value = initializer()
                isInitialized = true
            }
            return value!!
        }
        
        fun reset() {
            value = null
            isInitialized = false
        }
        
        fun isInitialized() = isInitialized
    }
    
    /**
     * Memory usage monitor for debugging
     */
    object MemoryMonitor {
        fun getMemoryInfo(): MemoryInfo {
            val runtime = Runtime.getRuntime()
            val totalMemory = runtime.totalMemory()
            val freeMemory = runtime.freeMemory()
            val usedMemory = totalMemory - freeMemory
            val maxMemory = runtime.maxMemory()
            
            return MemoryInfo(
                usedMemoryMB = usedMemory / (1024 * 1024),
                totalMemoryMB = totalMemory / (1024 * 1024),
                maxMemoryMB = maxMemory / (1024 * 1024),
                freeMemoryMB = freeMemory / (1024 * 1024),
                usagePercentage = (usedMemory.toDouble() / maxMemory * 100).toInt()
            )
        }
        
        data class MemoryInfo(
            val usedMemoryMB: Long,
            val totalMemoryMB: Long,
            val maxMemoryMB: Long,
            val freeMemoryMB: Long,
            val usagePercentage: Int
        )
    }
}