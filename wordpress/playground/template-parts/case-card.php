<?php $id = get_the_ID(); ?>
<a class="case-card reveal" href="<?php the_permalink(); ?>" data-category="<?php echo esc_attr( preg_replace( '/-pt$/', '', pg_term_slug( $id, 'pg_category' ) ) ); ?>" data-sector="<?php echo esc_attr( preg_replace( '/-pt$/', '', pg_term_slug( $id, 'pg_sector' ) ) ); ?>">
<?php echo pg_case_media( $id ); // phpcs:ignore ?>
<div class="case-body"><div class="tag"><?php echo esc_html( pg_case( 'tag' ) ); ?></div><h3><?php the_title(); ?></h3><p><?php echo esc_html( get_the_excerpt() ); ?></p>
<div class="case-result"><strong><?php pg_e( 'ui.read_case' ); ?> →</strong></div></div></a>
