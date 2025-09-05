package com.viaductecho.android.ui.articles

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.viaductecho.android.R
import com.viaductecho.android.data.models.Article
import com.viaductecho.android.databinding.ItemArticleBinding
import com.viaductecho.android.utils.DateUtils
import com.viaductecho.android.utils.loadImage

class ArticleListAdapter(
    private val onArticleClick: (Article) -> Unit
) : ListAdapter<Article, ArticleListAdapter.ArticleViewHolder>(ArticleDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ArticleViewHolder {
        val binding = ItemArticleBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ArticleViewHolder(binding, onArticleClick)
    }
    
    override fun onBindViewHolder(holder: ArticleViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
    
    class ArticleViewHolder(
        private val binding: ItemArticleBinding,
        private val onArticleClick: (Article) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {
        
        fun bind(article: Article) {
            binding.apply {
                // Set article title
                textViewTitle.text = article.title
                
                // Set source information
                textViewSource.text = article.source
                
                // Set published date
                textViewDate.text = DateUtils.formatRelativeTime(article.publishedDate)
                
                // Load article image
                imageViewArticle.loadImage(
                    url = article.imageUrl,
                    placeholder = R.drawable.placeholder_article,
                    error = R.drawable.error_image
                )
                
                // Set content description for accessibility
                imageViewArticle.contentDescription = 
                    root.context.getString(R.string.cd_article_image)
                
                // Handle click events
                root.setOnClickListener {
                    onArticleClick(article)
                }
                
                // Add ripple effect and proper touch feedback
                root.isClickable = true
                root.isFocusable = true
                
                // Set up source label styling
                textViewSource.apply {
                    setBackgroundResource(R.color.source_label_background)
                    setPadding(
                        resources.getDimensionPixelSize(R.dimen.padding_small),
                        resources.getDimensionPixelSize(R.dimen.padding_small) / 2,
                        resources.getDimensionPixelSize(R.dimen.padding_small),
                        resources.getDimensionPixelSize(R.dimen.padding_small) / 2
                    )
                }
            }
        }
    }
    
    class ArticleDiffCallback : DiffUtil.ItemCallback<Article>() {
        override fun areItemsTheSame(oldItem: Article, newItem: Article): Boolean {
            return oldItem.id == newItem.id
        }
        
        override fun areContentsTheSame(oldItem: Article, newItem: Article): Boolean {
            return oldItem == newItem
        }
    }
}