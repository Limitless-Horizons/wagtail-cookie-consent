# Change the colors

The banner's colors come from vanilla-cookieconsent's CSS variables. Set them in your own stylesheet, loaded after `{% cookie_consent %}`:

```css
#cc-main {
  --cc-bg: #ffffff;
  --cc-primary-color: #1f2937;
  --cc-btn-primary-bg: #0f766e;
  --cc-btn-primary-hover-bg: #115e59;
}
```

Its [documentation](https://cookieconsent.orestbida.com/advanced/ui-customization.html) lists the variables.
