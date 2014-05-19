<%inherit file="base.mako"/>

<%block name="content">
    <div class="container">
        <div class="panel panel-default">
            <div class="panel-heading">
                % if is_edit:
                    <h1>Edit User Profile</h1>
                % else:
                    <h1>Register User</h1>
                % endif
            </div>
            <div class="panel-body">
                ${form.render()|n}
            </div>
        </div>
    </div>
</%block>
