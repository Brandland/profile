<?php get_header(); ?>
<section class="page-hero"><div class="container"><div class="eyebrow orange">404</div><h1 class="h1" data-split><?php echo 'pt' === pg_lang() ? 'Esta página não existe.' : 'This page does not exist.'; ?></h1>
<div class="hero-actions"><a class="btn primary magnetic" href="<?php echo esc_url( pg_url( 'index' ) ); ?>"><?php pg_e( 'ui.nav.index' ); ?> <span class="arrow">→</span></a></div></div></section>
<?php get_footer(); ?>
