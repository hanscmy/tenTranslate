if (!(U(n).is(":hidden") || "SCRIPT" == n.nodeName || "LINK" == n.nodeName || "STYLE" == n.nodeName || "CODE" == n.nodeName || "NOSCRIPT" == n.nodeName || "CITE" == n.nodeName || n.classList && (n.classList.contains(H) || n.classList.contains(G) || n.classList.contains("qq_face") || n.classList.contains("msg_input_wrapper") || n.classList.contains("prettyprint") || n.classList.contains("PROGRAMLISTING"))))
							for (var r = n.childNodes, i = 0, o = r.length; i < o; i++) {
								var a = r[i];
								if (a && (!a.classList || !a.classList.contains(H) && !a.classList.contains(G)))
									if (a.classList && (a.classList.contains("js_message_plain") || a.classList.contains("message_body")))
										U(r[i]).children("." + G).length > 0 || (t(a), u.push(a));
									else if ("PRE" != a.nodeName)
										if ("P" != a.nodeName) {
											if (w(a)) {
												if (a.nodeName.indexOf("H") >= 0 && ("H1" == a.nodeName || "H2" == a.nodeName || "H3" == a.nodeName || "H4" == a.nodeName || "H5" == a.nodeName || "H6" == a.nodeName) && !(a.firstElementChild && ("SPAN" == a.firstElementChild.nodeName || "SPAN" == a.lastElementChild.nodeName || "A" == a.firstElementChild.nodeName || "A" == a.lastElementChild.nodeName) || a.parentElement && "A" == a.parentElement.nodeName)) {
													C(a, H),
													l.push(a);
													continue
												}
												if (!("SPAN" != a.nodeName && "LABEL" != a.nodeName && "LI" != a.nodeName || a.firstElementChild && "STRONG" != a.firstElementChild.nodeName)) {
													C(a, H),
													p.push(a);
													continue
												}
												if ("A" == a.nodeName && (!a.firstElementChild || "STRONG" == a.firstElementChild.nodeName)) {
													C(a, H),
													c.push(a);
													continue
												}
											}
                                            debugger;
											a.nodeType === Node.TEXT_NODE && T(a) ? (C(a.parentElement, H), m.push(a)) : a.nodeType === Node.ELEMENT_NODE && e(a)
										} else
											C(a, H), s.push(a)
							}