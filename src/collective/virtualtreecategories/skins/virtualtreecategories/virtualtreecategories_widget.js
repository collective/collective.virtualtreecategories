
(function($) {
    $(function() { 
        function selected_category(node) {
            var category = jq(node);
            var category_path = [];
            if (category != null) {
                category_path.push(category.attr('id'));
                category.parents('li').each(function() {
                    category_path.push(jq(this).attr('id'))
                });
            };
            return category_path;
        };
        function category_selected_deselected(node, tree_obj, selected_selector, unselected_selector, deselecting) {
            var selected_keywords = [];
            jq(selected_selector+' option').each(function() { 
                selected_keywords.push(this.value)
            });
            var selected_categories = [];
            var node_category_str = selected_category(node).join(',');
            jq.each(tree_obj.selected_arr, function() {
                sc = selected_category(this);
                if (deselecting) {
                    if (sc.join(',') == node_category_str) {
                        // skip currently deselected node
                        return
                    }
                } 
                selected_categories[selected_categories.length] = sc;
            });
            jq.ajax({
                    type:'POST',
                    url:portal_url+'/vtc-list-keywords_by_categories',
                    data:{  categories: selected_categories,
                            selected: selected_keywords
                         },
                    success:function(data) {
                                var $master = jq(unselected_selector);
                                $master.empty();
                                jq.each(data.keywords, function() { $master.append('<option value="'+this+'">'+this+'</option>') });
                            },
                    dataType: 'json',
                    traditional: true
            })
        };
        $(document).ready(function () {
            var $tree = jq('ul#VTCFilterTree');
            var widgetid = $tree.attr('data-widgetid');
            var widgettype = $tree.attr('data-widgettype');
            if (widgettype == 'archetypes') {
                var selected_selector = 'select#'+widgetid+'_selected';
                var unselected_selector = 'select#'+widgetid+'_unselected';
            } else if (widgettype == 'dexterity') {
                var selected_selector = 'select#'+widgetid+'-to';
                var unselected_selector = 'select#'+widgetid+'-from';
            }
            $tree.tree({
                        data  : {
                          type  : "json",
                          url   : portal_url+"/@@vtc-categories-tree.json",
                          async : false
                        },
                        ui : {
                               context: false
                        },
                        rules: {
                            multiple   : "on",
                            clickable  : [ "folder" ],
                            deletable  : "none",
                            renameable : "none",
                            creatable  : "none",
                            draggable  : "none",
                            droppable  : "none"
                        },
                        callback : {
                            onselect   : function(node, tree_obj) {
                                            category_selected_deselected(node, tree_obj, selected_selector, unselected_selector, false);
                                         },
                            ondeselect : function(node, tree_obj) {
                                            category_selected_deselected(node, tree_obj, selected_selector, unselected_selector, true);
                                         }
                        } 
                    });
            });
        })
})(jQuery);