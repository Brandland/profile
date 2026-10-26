<?php
/** Fallback template. */
get_header();
while ( have_posts() ) : the_post(); ?>
<section class="page-hero"><div class="container"><h1 class="h1" data-split><?php the_title(); ?></h1><?php if ( has_excerpt() ) : ?><p class="lead reveal"><?php echo esc_html( get_the_excerpt() ); ?></p><?php endif; ?></div></section>
<section class="section tight"><div class="container"><div class="article plain"><?php the_content(); ?></div></div></section>
<?php endwhile; get_footer();
