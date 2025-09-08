package com.viaductecho.android.ui.common

import android.content.Context
import android.util.AttributeSet
import android.view.LayoutInflater
import android.widget.FrameLayout
import com.viaductecho.android.R
import com.viaductecho.android.databinding.ViewLoadingStateBinding

/**
 * Reusable loading state component with consistent styling
 */
class LoadingStateView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr) {
    
    private val binding = ViewLoadingStateBinding.inflate(
        LayoutInflater.from(context), this, true
    )
    
    init {
        setupView(attrs)
    }
    
    private fun setupView(attrs: AttributeSet?) {
        attrs?.let {
            val typedArray = context.obtainStyledAttributes(it, R.styleable.LoadingStateView)
            
            // Set loading message if provided
            val loadingMessage = typedArray.getString(R.styleable.LoadingStateView_loadingMessage)
            if (!loadingMessage.isNullOrBlank()) {
                binding.textViewLoadingMessage.text = loadingMessage
            }
            
            typedArray.recycle()
        }
    }
    
    fun setLoadingMessage(message: String) {
        binding.textViewLoadingMessage.text = message
    }
    
    fun showLoading(show: Boolean = true) {
        visibility = if (show) VISIBLE else GONE
    }
}