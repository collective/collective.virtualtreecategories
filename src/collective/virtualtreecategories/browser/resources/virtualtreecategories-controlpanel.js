var keywords_changed = false;

function node_selected(node) {
    if (node.id == 'root-node') {
        jq("#keywords").hide()
    } else {
        jq("#keywords").show()
    };
    var ctitle = jq(node).find('a:first').text();
    jq('#selected-category-title').text(ctitle);
    keywords_changed = false;
    // call portal and get list of selected keywords
    jq.ajax({
         type: 'POST',
         url: "vtc-category-keywords",
         data: 
            {
              'category_path': selected_category(),
            },
         success :  
            function(plone_keywords){
                var keywords = plone_keywords.keywords;
                jq("#keywords select option").each(function(idx, obj) {
                    if (jQuery.inArray(this.value, keywords) != -1) {
                        jq(this).attr('selected', 'selected')
                    } else {
                        jq(this).removeAttr('selected')
                    }
                });
                if (keywords.length > 0) {
                    jq("#assigned-keywords-list").html(keywords.join(', '));
                    jq("#assigned-keywords").show();
                } else {
                    jq("#assigned-keywords-list").empty();
                    jq("#assigned-keywords").hide();
                };
                update_search_link();
            },
         dataType: 'json',
         traditional: true
    });
};
function update_search_link() {
    var $search_link = jq("#search-by-keywords-link");
    var search_base_url = jq("#search-by-keywords-link").attr('data-searchbaseurl');
    var keywords = jq("#keywords select").val();
    if (keywords !== null) {
        if (keywords.length > 0) {
            var query = "";
            jq.each(keywords, function(idx, kw) {
                query = query + encodeURIComponent("Subject:list")+"="+encodeURIComponent(kw) + "&";
            });
            $search_link.attr('href', search_base_url + '?' + query+"sort_order=reverse&sort_on=Date&"+encodeURIComponent("Subject_usage:ignore_empty="));
            $search_link.show();
        } else {
            $search_link.attr('href', "#");
            $search_link.hide();
        }
    } else {
        $search_link.attr('href', "#");
        $search_link.hide();
    }
};
function before_change_node() {
    if (keywords_changed) {
        if (confirm('Loose changes?')) {
            return true;
        } else {
            return false;
        }
    }
};
function selected_category(node) {
    if (node == undefined) {
        var category = jq.tree_reference('VTCTree').selected;
    } else {
        var category = jq(node);
    };
    var category_path = [];
    if (category != null) {
        category_path.push(category.attr('id'));
        category.parents('li').each(function() {
            category_path.push(jq(this).attr('id'))
        });
    };
    return category_path;
};
jq(document).ready(function () {
    var $tree = jq('ul#VTCTree');

    jq('#keywords').bind('change', function() {
        keywords_changed = true;
        var node = jq.tree_reference('VTCTree').selected;
        var ctitle = node.find('a:first').text();
        jq('#selected-category-title').text(ctitle);
        jq('#save-area').show();
        update_search_link();
    });

    jq('#save-keywords').bind('click', function() {
        // send list of selected keywords to the server
        var kws = [];
        jq("#keywords select option").each(function() {
            var selected = jq(this).attr('selected');
            if (selected || (selected == 'selected')) {
                kws.push(jq(this).text());
            }
        });
        var category = selected_category();
        if (category == null) {
            jq.jGrowl('No category selected', { life: 1500 });
        } else {
            jq.ajax({
                 type: 'POST',
                 url: "vtc-category-save-keywords",
                 data: 
                    {
                        'category_path': category,
                        'kws': kws
                    },
                 success :  
                    function(data) {
                        jq.jGrowl(data.message, { life: 1500 });
                        keywords_changed = false;
                        jq('#save-area').hide();
                        if (data.keywords.length > 0) {
                            jq("#assigned-keywords-list").html(data.keywords.join(', '));
                            jq("#assigned-keywords").show();
                        } else {
                            jq("#assigned-keywords-list").empty();
                            jq("#assigned-keywords").hide();
                        }
                    },
                 dataType: 'json',
                 traditional: true
            })
        }
    });

    $tree.tree({
                    data  : {
                      type  : "json",
                      url   : "@@vtc-categories-tree.json",
                      async : false
                    },
                    lang : {
                        new_node    : "New category"
                    },
                    rules: {
                        deletable  : [ "folder" ],
                        renameable : [ "folder" ],
                        draggable  : "none",
                        droppable  : "none",
                    },
                    callback: {
                        beforechange: function(node, tree_obj) { return before_change_node() },
                        onselect: function(node, tree_obj) { node_selected(node) },
                        oncreate: function(node) { jq(node).attr('rel', 'folder') },
                        onrename: function(node, lang, tree_obj, rb) {
                            old_id = node.id // may be undefined (new node)
                            new_name = jq(node).children("a:visible").text();
                            // shared code. Server determines if creating/renaming by the old_name value
                            jq.ajax({
                                 type: 'POST',
                                 url: "vtc-category-added-renamed",
                                 data: 
                                    {
                                      'category_path': selected_category(node),
                                      'old_id': old_id,
                                      'new_name': new_name
                                    },
                                 success :  
                                    function(data) {
                                        jq.jGrowl(data.msg, { life: 1500 });
                                        // set/change node id
                                        if (data.result) {
                                            node.id = data.new_id
                                        }
                                    },
                                 dataType: 'json',
                                 traditional: true
                            })
                        },
                        beforedelete: function(node, tree_obj) {
                            jq.ajax({
                                 type: 'POST',
                                 url: "vtc-category-removed",
                                 data: 
                                    {
                                      'category_path': selected_category(node)
                                    },
                                 success :  
                                    function(data) {
                                        jq.jGrowl(data.msg, { life: 3000 });
                                    },
                                 dataType: 'json',
                                 traditional: true
                            });
                            return true;
                        } 
                    }
    });
    // unassigned keywords
    jq(".unassigned-keyword").click(function(event) {
        event.preventDefault(); 
        event.stopPropagation();
        var data = jq(this).attr("data-count");
        var $item = jq(this);
        if (data===undefined) {
            jq.get('@@vtc-content-count', 
                   {
                       kw : encodeURIComponent($item.attr("data-kw"))
                   },
                   function(data) {
                       link_url = '<a target="_blank" href="'+portal_url+'/search?Subject='+encodeURIComponent($item.attr("data-kw"))+'">'+$item.attr("data-kw") + " <span>("+data+")</span>"+'</a>';
                       $item.html(link_url);
                       $item.attr("data-count", data);
                       $item.unbind('click');
                   });
        } else {
            link_url = '<a target="_blank" href="'+portal_url+'/search?Subject='+encodeURIComponent($item.attr("data-kw"))+'">'+$item.attr("data-kw") + " <span>("+data+")</span>"+'</a>';
            $item.html(link_url);
            $item.unbind('click');
        }
    });
});
            
