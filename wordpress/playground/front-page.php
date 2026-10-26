<?php
/** Home page. Copy from content/{lang}.json; work and insights from WordPress. */
get_header();
$h = pg_t( 'home' );
?>
<section class="hero">
<svg class="hero-orbit" viewBox="0 0 1440 800" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
<path d="M-40 760 C 340 520, 820 380, 1500 300"/><path class="thin" d="M120 820 C 420 560, 900 420, 1480 380"/><path d="M760 180 C 1000 120, 1260 180, 1400 330"/><circle cx="1180" cy="210" r="4"/>
</svg>
<div class="container hero-grid"><div class="hero-copy">
<div class="hero-kicker eyebrow reveal"><?php echo esc_html( $h['kicker'] ); ?></div>
<h1 class="display" data-split><?php echo wp_kses( $h['title_html'], array( 'span' => array( 'class' => array() ) ) ); ?></h1>
<p class="lead reveal" style="margin-top:28px"><?php echo esc_html( $h['lead'] ); ?></p>
<div class="hero-actions reveal"><a class="btn primary magnetic" href="<?php echo esc_url( pg_url( 'contact' ) ); ?>"><?php echo esc_html( $h['cta_primary'] ); ?> <span class="arrow">↗</span></a><a class="btn ghost magnetic" href="<?php echo esc_url( pg_url( 'work' ) ); ?>"><?php echo esc_html( $h['cta_secondary'] ); ?> <span class="arrow">→</span></a></div>
<div class="hero-proof reveal"><?php foreach ( $h['proof'] as $p ) : ?><div class="proof"><strong data-count="<?php echo esc_attr( $p['value'] ); ?>" data-suffix="<?php echo esc_attr( $p['suffix'] ); ?>"><?php echo esc_html( $p['value'] . $p['suffix'] ); ?></strong><span><?php echo esc_html( $p['label'] ); ?></span></div><?php endforeach; ?></div>
</div></div><span class="orbit-float" aria-hidden="true"></span></section>

<div class="band" aria-hidden="true"><div class="marquee"><?php for ( $r = 0; $r < 2; $r++ ) { foreach ( $h['marquee'] as $m ) { echo '<span><b>' . esc_html( $m ) . '</b></span><span class="dot">✦</span>'; } } ?></div></div>

<section class="section"><div class="container">
<div class="section-head"><div><div class="eyebrow orange reveal"><?php echo esc_html( $h['services_eyebrow'] ); ?></div><h2 class="h2" data-split style="margin-top:14px"><?php echo esc_html( $h['services_title'] ); ?></h2></div><p class="lead reveal"><?php echo esc_html( $h['services_lead'] ); ?></p></div>
<div class="service-grid" data-stagger><?php foreach ( pg_t( 'services', array() ) as $i => $s ) : ?>
<a class="service-card spot reveal" href="<?php echo esc_url( pg_url( 'expertise' ) . '#' . $s['slug'] ); ?>"><div><div class="service-index"><?php printf( '%02d', $i + 1 ); ?></div><h3 class="h3" style="font-size:24px;margin-top:40px"><?php echo esc_html( $s['title'] ); ?></h3><p><?php echo esc_html( $s['text'] ); ?></p></div><div class="more"><?php pg_e( 'ui.read_more' ); ?> <span>→</span></div></a>
<?php endforeach; ?></div></div></section>

<?php $work = new WP_Query( array( 'post_type' => 'case_study', 'posts_per_page' => 4, 'orderby' => array( 'menu_order' => 'ASC', 'date' => 'DESC' ) ) ); if ( $work->have_posts() ) : ?>
<section class="section soft"><div class="container">
<div class="section-head"><div><div class="eyebrow orange reveal"><?php echo esc_html( $h['work_eyebrow'] ); ?></div><h2 class="h2" data-split style="margin-top:14px"><?php echo esc_html( $h['work_title'] ); ?></h2></div><div><p class="lead reveal"><?php echo esc_html( $h['work_lead'] ); ?></p><a class="btn ghost magnetic reveal" style="margin-top:22px" href="<?php echo esc_url( pg_url( 'work' ) ); ?>"><?php pg_e( 'ui.view_all_work' ); ?> <span class="arrow">→</span></a></div></div>
<div class="work-grid"><?php $sizes = array( 'large', 'small', 'small', 'large' ); $n = 0; while ( $work->have_posts() ) : $work->the_post(); $media = has_post_thumbnail() ? 'dark' : ( pg_case( 'media' ) ? pg_case( 'media' ) : 'dark' ); ?>
<a class="work-card <?php echo esc_attr( $sizes[ $n % 4 ] . ' ' . $media ); ?> reveal-clip" href="<?php the_permalink(); ?>"><?php if ( has_post_thumbnail() ) : ?><div class="bg" style="background-image:url(<?php echo esc_url( get_the_post_thumbnail_url( null, 'pg-card' ) ); ?>)"></div><?php else : ?><div class="bg"></div><?php endif; ?>
<div class="content"><div class="tag"><?php echo esc_html( pg_case( 'tag' ) ); ?></div><h3><?php the_title(); ?></h3><p><?php echo esc_html( get_the_excerpt() ); ?></p><span class="go"><?php pg_e( 'ui.read_case' ); ?> <span>→</span></span></div></a>
<?php $n++; endwhile; wp_reset_postdata(); ?></div></div></section>
<?php endif; ?>

<section class="section dark"><div class="container">
<div class="eyebrow orange reveal"><?php echo esc_html( $h['metrics_eyebrow'] ); ?></div><h2 class="h2" data-split style="margin-top:14px;max-width:900px"><?php echo esc_html( $h['metrics_title'] ); ?></h2>
<div class="metrics reveal"><?php foreach ( $h['metrics'] as $m ) : ?><div class="metric"><strong data-count="<?php echo esc_attr( $m['value'] ); ?>" data-suffix="<?php echo esc_attr( $m['suffix'] ); ?>"><?php echo esc_html( $m['value'] . $m['suffix'] ); ?></strong><span><?php echo esc_html( $m['label'] ); ?></span></div><?php endforeach; ?></div></div></section>

<section class="section"><div class="container">
<div class="section-head"><div><div class="eyebrow orange reveal"><?php echo esc_html( $h['sectors_eyebrow'] ); ?></div><h2 class="h2" data-split style="margin-top:14px"><?php echo esc_html( $h['sectors_title'] ); ?></h2></div><p class="lead reveal"><?php pg_e( 'sectors_page.intel_lead' ); ?></p></div>
<div class="sector-list" data-stagger><?php foreach ( pg_t( 'sectors', array() ) as $i => $s ) : ?><a class="sector reveal" href="<?php echo esc_url( pg_url( 'work' ) . '#' . $s['slug'] ); ?>"><span class="num"><?php printf( '%02d', $i + 1 ); ?></span><span class="name"><?php echo esc_html( $s['name'] ); ?></span><span class="arr">↗</span></a><?php endforeach; ?></div>
</div></section>

<section class="section soft"><div class="container">
<div class="section-head"><div><div class="eyebrow orange reveal"><?php echo esc_html( $h['insights_eyebrow'] ); ?></div><h2 class="h2" data-split style="margin-top:14px"><?php echo esc_html( $h['insights_title'] ); ?></h2></div></div>
<?php get_template_part( 'template-parts/insights-grid' ); ?>
</div></section>

<?php get_template_part( 'template-parts/linkedin' ); ?>
<?php get_template_part( 'template-parts/cta' ); ?>
<?php get_footer(); ?>
