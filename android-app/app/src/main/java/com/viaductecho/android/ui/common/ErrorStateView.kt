package com.viaductecho.android.ui.common

import android.content.Context
import android.util.AttributeSet
import android.view.LayoutInflater
import android.widget.FrameLayout
import com.viaductecho.android.R
import com.viaductecho.android.databinding.ViewErrorStateBinding

/**
 * Reusable error state component with retry functionality
 */
class ErrorStateView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr) {

    private val binding = ViewErrorStateBinding.inflate(
        LayoutInflater.from(context), this, true
    )

    private var onRetryClickListener: (() -> Unit)? = null

    init {
        setupView(attrs)
        binding.buttonRetry.setOnClickListener {
            onRetryClickListener?.invoke()
        }
    }

    private fun setupView(attrs: AttributeSet?) {
        attrs?.let {
            val typedArray = context.obtainStyledAttributes(it, R.styleable.ErrorStateView)

            // Set error message if provided
            val errorMessage = typedArray.getString(R.styleable.ErrorStateView_errorMessage)
            if (!errorMessage.isNullOrBlank()) {
                binding.textViewErrorMessage.text = errorMessage
            }

            // Set error icon if provided
            val errorIcon = typedArray.getDrawable(R.styleable.ErrorStateView_errorIcon)
            if (errorIcon != null) {
                binding.imageViewErrorIcon.setImageDrawable(errorIcon)
            }

            typedArray.recycle()
        }
    }

    fun setErrorMessage(message: String) {
        binding.textViewErrorMessage.text = message
    }

    fun setErrorIcon(iconRes: Int) {
        binding.imageViewErrorIcon.setImageResource(iconRes)
    }

    fun setOnRetryClickListener(listener: () -> Unit) {
        onRetryClickListener = listener
    }

    fun showError(show: Boolean = true) {
        visibility = if (show) VISIBLE else GONE
    }

    fun showRetryButton(show: Boolean = true) {
        binding.buttonRetry.visibility = if (show) VISIBLE else GONE
    }
}
