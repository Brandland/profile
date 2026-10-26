<?php
$q = new WP_Query( array( 'posts_per_page' => 3, 'ignore_sticky_posts' => false ) );
if ( ! $q->have_posts() ) { return; }
$i = 0;
echo '<div class="insights-grid">';
while ( $q->have_posts() ) :
	$q->the_post();
	$cat = get_the_category();
	$tag = $cat ? $cat[0]->name : '';
	if ( 0 === $i ) :
		$bg = has_post_thumbnail() ? ',url(' . esc_url( get_the_post_thumbnail_url( null, 'pg-cover' ) ) . ') center/cover' : '';
		?>
<a class="insight-feature reveal" href="<?php the_permalink(); ?>"<?php echo $bg ? ' style="background:linear-gradient(180deg,rgba(10,10,10,.05),rgba(10,10,10,.86))' . $bg . '"' : ''; // phpcs:ignore ?>><div class="eyebrow orange"><?php echo esc_html( $tag ); ?></div><h2><?php the_title(); ?></h2><p><?php echo esc_html( get_the_excerpt() ); ?></p><div style="margin-top:20px;font-size:13px"><?php echo (int) pg_reading_time(); ?> <?php pg_e( 'ui.min_read' ); ?> · <?php pg_e( 'ui.read_more' ); ?> ↗</div></a>
<div class="insight-side" data-stagger>
	<?php else : ?>
<a class="insight-card reveal" href="<?php the_permalink(); ?>"><div><div class="eyebrow orange"><?php echo esc_html( $tag ); ?></div><h3><?php the_title(); ?></h3><p><?php echo esc_html( get_the_excerpt() ); ?></p></div><span><?php echo (int) pg_reading_time(); ?> <?php pg_e( 'ui.min_read' ); ?> ↗</span></a>
		<?php
	endif;
	$i++;
endwhile;
echo '</div></div>';
wp_reset_postdata();
