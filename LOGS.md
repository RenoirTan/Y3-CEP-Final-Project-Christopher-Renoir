# Read this for additions to Students Gateway

`/login`, `/logout`, `/invalid-login` added

If you want to redirect with different apps, use:

```python
	return redirect(url_for("<appname>.<functionname>"))
	# Example
	return redirect(url_for("apiget.get_student"))
```

